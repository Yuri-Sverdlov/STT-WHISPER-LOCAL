# -*- coding: utf-8 -*-
"""
dictate.py -- thin voice-dictation script on faster-whisper (track approach).

Bypasses the whisper-local GUI wrapper (which swallows a cuBLAS RuntimeError and
hangs on "transcribing"). Must run in the SAME Python where the direct GPU test
passed (whisper-local bundled interpreter), so cuBLAS DLLs sit next to ctranslate2.

Flow (single-key toggle, default):
  Ctrl+Space  -> start microphone recording (sounddevice, 16 kHz mono)
  Ctrl+Space  -> stop -> transcribe (faster-whisper) -> paste at cursor
Paste is clipboard-based (pyperclip + emulated Ctrl+V) -- robust for Cyrillic.
Two-key mode is available via --stop-key (e.g. --stop-key f8).

Design rules (AGENTS.md):
  - Model is loaded and called in ONE dedicated worker thread via a queue,
    never from a hotkey callback.
  - Paths derive from HERE; external paths are CLI params with defaults.
  - print() uses ASCII only ("->"); files are UTF-8.
"""

import argparse
import queue
import sys
import threading
import time
from pathlib import Path

import numpy as np
import sounddevice as sd
import pyperclip
import keyboard

HERE = Path(__file__).resolve().parent

# Sentinel put on the job queue to tell the worker to shut down.
_STOP = object()


def log(msg):
    """ASCII-only stdout line, flushed (DEV-NOTES: tool prints work done)."""
    print(msg, flush=True)


class Recorder:
    """Microphone capture into an in-memory float32 mono buffer.

    start()/stop() are safe to call from a hotkey callback thread; the model
    never touches this class -- stop() only hands raw audio to the job queue.
    """

    def __init__(self, samplerate, jobs, device=None):
        self.samplerate = samplerate
        self.jobs = jobs
        self.device = device  # input device index or None (system default)
        self._stream = None
        self._frames = []
        self._lock = threading.Lock()
        self.recording = False
        self._last_toggle = 0.0  # debounce against key auto-repeat

    def _callback(self, indata, frames, time_info, status):
        if status:
            # Overflows etc. -- note but keep capturing.
            log("WARN audio status: " + str(status))
        with self._lock:
            self._frames.append(indata.copy())

    def start(self):
        if self.recording:
            return
        with self._lock:
            self._frames = []
        try:
            self._stream = sd.InputStream(
                samplerate=self.samplerate,
                channels=1,
                dtype="float32",
                device=self.device,
                callback=self._callback,
            )
            self._stream.start()
        except Exception as exc:  # noqa: BLE001 -- surface any device error
            log("ERROR cannot open microphone: " + str(exc))
            self._stream = None
            return
        self.recording = True
        try:
            name = sd.query_devices(self._stream.device, "input")["name"]
        except Exception:  # noqa: BLE001
            name = str(self.device)
        log("REC start on [%s] -- speak, then press the hotkey again to stop" % name)

    def toggle(self):
        """Single-key toggle: start if idle, else stop -> transcribe.

        Debounced: a second trigger within 0.3s (key auto-repeat) is ignored,
        so holding the hotkey does not immediately start-then-stop.
        """
        now = time.time()
        if now - self._last_toggle < 0.3:
            return
        self._last_toggle = now
        if self.recording:
            self.stop()
        else:
            self.start()

    def stop(self):
        if not self.recording:
            return
        self.recording = False
        try:
            self._stream.stop()
            self._stream.close()
        finally:
            self._stream = None
        with self._lock:
            frames = self._frames
            self._frames = []
        if not frames:
            log("REC stop -> no audio captured, skipped")
            log("HINT mic delivered 0 frames. Another app may hold the microphone "
                "(e.g. Wispr Flow in the tray) -- close it. Or pick a device: "
                "--list-devices then --device-index N")
            return
        audio = np.concatenate(frames, axis=0).reshape(-1).astype("float32")
        secs = len(audio) / float(self.samplerate)
        peak = float(np.max(np.abs(audio))) if audio.size else 0.0
        log("REC stop -> queued %.2fs of audio (peak=%.3f)" % (secs, peak))
        if peak < 0.01:
            log("WARN signal is near-silent (peak=%.3f) -- mic may be muted or held "
                "by another app; Whisper will hallucinate on silence" % peak)
        if secs < 0.3:
            log("SKIP clip shorter than 0.3s")
            return
        self.jobs.put(audio)


def transcribe_worker(jobs, ready, args):
    """Dedicated thread: load model once, then transcribe queued clips."""
    try:
        from faster_whisper import WhisperModel
    except Exception as exc:  # noqa: BLE001
        log("FATAL cannot import faster_whisper: " + str(exc))
        ready.set()
        return

    log("MODEL loading %s device=%s compute=%s ..." % (args.model, args.device, args.compute_type))
    t0 = time.time()
    try:
        model_kwargs = dict(device=args.device, compute_type=args.compute_type)
        if args.model_dir:
            model_kwargs["download_root"] = args.model_dir
        model = WhisperModel(args.model, **model_kwargs)
    except Exception as exc:  # noqa: BLE001
        log("FATAL model load failed: " + str(exc))
        log("HINT try CPU fallback: --device cpu --compute-type int8 --model small")
        ready.set()
        return
    log("MODEL_LOADED init=%.2fs" % (time.time() - t0))
    ready.set()

    while True:
        job = jobs.get()
        if job is _STOP:
            return
        audio = job
        t0 = time.time()
        try:
            segments, info = model.transcribe(
                audio,
                language=args.language,
                beam_size=args.beam_size,
            )
            text = "".join(seg.text for seg in segments).strip()
        except Exception as exc:  # noqa: BLE001
            log("ERROR transcribe failed: " + str(exc))
            continue
        took = time.time() - t0
        log("TRANSCRIBED took=%.2fs lang=%s chars=%d" % (took, info.language, len(text)))
        if not text:
            log("EMPTY no speech recognized, nothing pasted")
            continue
        _paste(text, args.paste)


def _paste(text, do_paste):
    """Copy to clipboard, then emulate Ctrl+V (robust for Cyrillic)."""
    try:
        pyperclip.copy(text)
    except Exception as exc:  # noqa: BLE001
        log("ERROR clipboard copy failed: " + str(exc))
        return
    if not do_paste:
        log("COPIED to clipboard (paste disabled) -- press Ctrl+V yourself")
        return
    # Small settle so the target app has focus and clipboard is ready.
    time.sleep(0.05)
    try:
        keyboard.send("ctrl+v")
        log("PASTED via Ctrl+V")
    except Exception as exc:  # noqa: BLE001
        log("WARN auto-paste failed (text is on clipboard): " + str(exc))


def build_argparser():
    p = argparse.ArgumentParser(
        description="Thin faster-whisper voice dictation (Ctrl+Space / F8).",
    )
    p.add_argument("--model", default="large-v3", help="whisper model (default: large-v3)")
    p.add_argument("--device", default="cuda", help="cuda | cpu (default: cuda)")
    p.add_argument("--compute-type", default="float16",
                   help="float16 | int8 | int8_float16 (default: float16)")
    p.add_argument("--language", default="ru", help="language code (default: ru)")
    p.add_argument("--beam-size", type=int, default=5, help="beam size (default: 5)")
    p.add_argument("--samplerate", type=int, default=16000, help="capture Hz (default: 16000)")
    p.add_argument("--device-index", type=int, default=None,
                   help="input device index (default: system default). See --list-devices.")
    p.add_argument("--list-devices", action="store_true",
                   help="print available audio devices and exit")
    p.add_argument("--start-key", default="ctrl+space",
                   help="start/toggle hotkey (default: ctrl+space)")
    p.add_argument("--stop-key", default="",
                   help="separate stop hotkey; empty = single-key toggle mode (default: toggle)")
    p.add_argument("--quit-key", default="ctrl+shift+q", help="quit hotkey (default: ctrl+shift+q)")
    p.add_argument("--model-dir", default=None,
                   help="model cache dir (default: HF cache). External path is a CLI arg.")
    paste = p.add_mutually_exclusive_group()
    paste.add_argument("--paste", dest="paste", action="store_true", default=True,
                       help="auto-paste via Ctrl+V (default)")
    paste.add_argument("--no-paste", dest="paste", action="store_false",
                       help="only copy to clipboard, do not press Ctrl+V")
    return p


def main(argv=None):
    args = build_argparser().parse_args(argv)

    if args.list_devices:
        log("Audio devices (index: name  [in/out channels]):")
        for i, d in enumerate(sd.query_devices()):
            mark = " <- default in" if i == sd.default.device[0] else ""
            log("  %2d: %s  [in=%d out=%d]%s"
                % (i, d["name"], d["max_input_channels"], d["max_output_channels"], mark))
        return 0

    jobs = queue.Queue()
    ready = threading.Event()
    worker = threading.Thread(target=transcribe_worker, args=(jobs, ready, args), daemon=True)
    worker.start()

    log("Waiting for model to load (first run downloads weights from HF)...")
    ready.wait()
    if not worker.is_alive():
        log("FATAL worker thread exited before ready -- see error above")
        return 1

    rec = Recorder(args.samplerate, jobs, device=args.device_index)

    stop_event = threading.Event()

    def on_quit():
        log("QUIT requested")
        stop_event.set()

    keyboard.add_hotkey(args.quit_key, on_quit)
    if args.stop_key:
        # Two-key mode: explicit start + stop.
        keyboard.add_hotkey(args.start_key, rec.start)
        keyboard.add_hotkey(args.stop_key, rec.stop)
        log("READY. %s = start | %s = stop+transcribe+paste | %s = quit"
            % (args.start_key, args.stop_key, args.quit_key))
    else:
        # Single-key toggle mode (default): press to start, press again to stop.
        keyboard.add_hotkey(args.start_key, rec.toggle)
        log("READY. %s = toggle rec (press to start, press again to stop+paste) | %s = quit"
            % (args.start_key, args.quit_key))
    log("Focus the target window (e.g. Notepad) before pasting.")

    try:
        stop_event.wait()
    except KeyboardInterrupt:
        log("Interrupted")
    finally:
        jobs.put(_STOP)
        worker.join(timeout=5)
    log("Bye")
    return 0


if __name__ == "__main__":
    sys.exit(main())
