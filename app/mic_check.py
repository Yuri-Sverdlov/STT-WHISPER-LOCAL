# -*- coding: utf-8 -*-
"""
mic_check.py -- isolate microphone capture from hotkeys / Whisper.

Records a few seconds from an input device and prints the signal level per
0.5s window plus the overall peak. Use it to tell "the app gets my voice" from
"the app gets digital silence" (Windows mic-privacy denial or a muted device).

Usage (bundled Python or run-dictate.ps1 style):
  python app/mic_check.py                 # default device, 4 seconds
  python app/mic_check.py --seconds 5 --device-index 1
  python app/mic_check.py --list-devices
"""

import argparse
import time

import numpy as np
import sounddevice as sd


def main():
    p = argparse.ArgumentParser(description="Microphone level check (no hotkeys, no Whisper).")
    p.add_argument("--seconds", type=float, default=4.0, help="record duration (default: 4)")
    p.add_argument("--samplerate", type=int, default=16000, help="capture Hz (default: 16000)")
    p.add_argument("--device-index", type=int, default=None, help="input device index")
    p.add_argument("--list-devices", action="store_true", help="print devices and exit")
    args = p.parse_args()

    if args.list_devices:
        for i, d in enumerate(sd.query_devices()):
            if d["max_input_channels"] > 0:
                mark = " <- default in" if i == sd.default.device[0] else ""
                print("  %2d: %s  [in=%d]%s" % (i, d["name"], d["max_input_channels"], mark), flush=True)
        return 0

    try:
        name = sd.query_devices(args.device_index, "input")["name"]
    except Exception as exc:  # noqa: BLE001
        print("ERROR cannot query input device: " + str(exc), flush=True)
        return 1

    print("Recording %.1fs from [%s] -- SPEAK NOW..." % (args.seconds, name), flush=True)
    frames = []

    def cb(indata, n, t, status):
        if status:
            print("WARN status: " + str(status), flush=True)
        frames.append(indata.copy())

    win = int(0.5 * args.samplerate)
    try:
        with sd.InputStream(samplerate=args.samplerate, channels=1, dtype="float32",
                            device=args.device_index, callback=cb):
            shown = 0
            t_end = time.time() + args.seconds
            while time.time() < t_end:
                time.sleep(0.05)
                total = sum(len(f) for f in frames)
                while total - shown >= win:
                    chunk = np.concatenate(frames).reshape(-1)[shown:shown + win]
                    shown += win
                    peak = float(np.max(np.abs(chunk))) if chunk.size else 0.0
                    bars = int(min(peak, 1.0) * 40)
                    print("  t=%4.1fs level %-40s peak=%.3f"
                          % (shown / args.samplerate, "#" * bars, peak), flush=True)
    except Exception as exc:  # noqa: BLE001
        print("ERROR opening mic: " + str(exc), flush=True)
        return 1

    if not frames:
        print("RESULT no frames at all -- device delivered nothing.", flush=True)
        return 2
    audio = np.concatenate(frames).reshape(-1)
    peak = float(np.max(np.abs(audio)))
    rms = float(np.sqrt(np.mean(audio ** 2)))
    print("RESULT samples=%d peak=%.4f rms=%.4f" % (len(audio), peak, rms), flush=True)
    if peak < 0.01:
        print("VERDICT near-silent -> Windows is feeding SILENCE. Check:", flush=True)
        print("  1) Settings > Privacy & security > Microphone:", flush=True)
        print("     'Microphone access' ON and 'Let desktop apps access your microphone' ON.", flush=True)
        print("  2) Settings > System > Sound > Input: pick LifeCam, volume up, not muted.", flush=True)
        print("  3) If you speak into another mic, use its index (--list-devices).", flush=True)
    else:
        print("VERDICT mic OK -- real signal captured. dictate.py should work now.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
