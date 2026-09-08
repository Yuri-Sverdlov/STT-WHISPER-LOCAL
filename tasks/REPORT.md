# REPORT — текущий отчёт (кодер -> архитектор)

Задание: развернуть трек A на GPU (RTX 4060).
Статус: **ВЫПОЛНЕНО и проверено вживую 2026-09-07.** Диктовка на GPU работает.

## Диагностика CUDA / PATH
- `nvidia-smi`: драйвер 581.57, CUDA Version 13.0, RTX 4060 (8188 MiB).
- Старый `cudart64_65.dll` (CUDA 6.5) от PhysX был в **Machine PATH** -> убран
  (`PhysX\Common`). CUDA Toolkit не ставился и не нужен (драйвер даёт CUDA 12+).

## Установка whisper-local
- v0.18.3 с GitHub. SHA256 `56cef2b71416fce31f69f3bec4d21d9a7a4f1fc93e383c4ca568a7701a7037fa`
  (winget упал на сертификате msstore; `.sha256` в релизе нет).
- Конфиг: device `cuda`, compute_type `float16`, model `large-v3`, language `ru`.

## Что НЕ работало и как починено
«GPU ready» ещё не значит «распознаёт»: модель грузилась, но реальная диктовка
падала/висла. Четыре причины, все устранены (подробно — PROJECT_LOG 2026-09-07):

1. `recording_hotkey: AltGr+/` -> краш (библиотека не знает `altgr`). Правый Alt/AltGr нельзя.
2. Символ `/` как клавиша не разбирается -> пустой ключ -> краш. Только буквы/space/F-клавиши.
3. Пустой `stop_key: ''` -> баг whisper-local (нет проверки) -> "key []" -> краш. Дан `f8`.
4. **Нет cuBLAS.** ctranslate2 несёт cuDNN, но не `cublas64_12.dll` -> encode бросает
   "Library cublas64_12.dll is not found", приложение виснет на "transcribing...".
   Лечение: `pip install nvidia-cublas-cu12` + копия `cublas64_12.dll`/`cublasLt64_12.dll`
   в папку `...\site-packages\ctranslate2\`.

## Итоговый конфиг (`%APPDATA%\whisperkey\user_settings.yaml`, пер-машинный)
```yaml
whisper:  { model: large-v3, device: cuda, compute_type: float16, language: ru }
hotkey:   { recording_hotkey: ctrl+space (hold-to-record), stop_key: f8,
            auto_send_key: alt+s, pause_hotkey: ctrl+alt+p }
```

## Тест — ПРОЙДЕН
- Прямой прогон faster_whisper на GPU: model load 3.3 с, transcribe 0.7 с (float16).
- Юрий вживую: Ctrl+Space -> продиктовал -> русский текст вставился в Блокнот.

## Чек-лист
- [x] Диагностика CUDA/PATH
- [x] Установка whisper-local, GPU float16, large-v3, ru
- [x] Хоткеи исправлены (ctrl+space, stop_key f8)
- [x] cuBLAS доставлен (главный блокер)
- [x] Тест диктовки — подтверждён пользователем
