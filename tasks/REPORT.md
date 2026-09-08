# REPORT — текущий отчёт (кодер -> архитектор)

Задание: `tasks/TASK.md` (ПК1, RTX 3050, sync + трек A).
Статус: **выполнено (GPU работает).**

## Sync с GitHub
- `git fetch origin`; HEAD == origin/main == `05f1dfe` (после fetch).
- Рабочее дерево: незакоммиченные правки канона (CONTEXT/TASK/REPORT/PROJECT_LOG) —
  это правки архитектора на ПК1, коммит — шаг 6.
- pull не понадобился (уже синхронно).

## Диагностика CUDA / PATH
- `nvidia-smi`: RTX 3050, **Driver 591.86, CUDA 13.1** (драйверный runtime — актуальный).
- `nvcc` нет, CUDA Toolkit не стоит (правильно).
- **Найден виновник «found CUDA 6.5»: `C:\Program Files (x86)\NVIDIA Corporation\PhysX\Common\cudart64_65.dll`** (+ cudart32_65.dll).
  Он в PATH и в User, и в Machine.
- **User PATH:** PhysX\Common убран (запись удалена; entries 46 -> 45). ✓
- **Machine PATH:** удаление заблокировано (нет прав без UAC/элевации). НЕ трогал —
  но **оказалось не нужно**: при размещении всех CUDA-12 DLL локально в ctranslate2\
  старый 6.5 в PATH не подхватывается (см. ниже).

## Установка whisper-local
- v0.18.3 уже скачан: `%USERPROFILE%\Downloads\whisper-local.exe`;
  sha256 `56cef2b71416fce31f69f3bec4d21d9a7a4f1fc93e383c4ca568a7701a7037fa` — совпадает. ✓
- Установка уже была (CPU base/int8, onboarding=done). Приложение использует встроенный
  Python `%LOCALAPPDATA%\Python\pythoncore-3.14-64` (site-packages: faster-whisper 1.2.1,
  ctranslate2 4.8.1).
- **cuBLAS (главная грабля, обязателен):** в ctranslate2 были cudnn64_9.dll, но не cuBLAS.
  Установлено и скопировано в `...\site-packages\ctranslate2\`:
  - `pip install nvidia-cublas-cu12` (12.9.2.10) -> `cublas64_12.dll`, `cublasLt64_12.dll`
  - `pip install nvidia-cuda-runtime-cu12` (12.9.79) -> `cudart64_12.dll`
  - Итог в ctranslate2\: cublas64_12, cublasLt64_12, cudart64_12 + cudnn64_9. ✓

## Конфиг (пер-машинный, НЕ в git)
`%APPDATA%\whisperkey\` — целевой GPU-профиль ПК1 (как на ПК2):
- `profiles.yaml`: активный профиль `dictation` -> whisper: large-v3, cuda, float16, ru;
  hotkey: recording_hotkey **ctrl+space**, stop_key **f8**, push_to_talk. Бэкап: *.bak-20260908.
- `user_settings.yaml`: те же whisper-параметры + hotkey-блок (мин. набор).
- Бэкапы: `user_settings.yaml.bak-20260908`, `profiles.yaml.bak-20260908` (в той же папке).

## Тест (проверено запуском, DEV-NOTES §16)
Прямой прогон faster_whisper через venv-python (пакетный, не GUI — рекомендация TASK):
```
DOWNLOAD_DONE
MODEL_LOADED  init=7.87s        (large-v3, cuda, float16)
TRANSCRIBED   took=1.09s lang=ru
RESULT_OK     text_len=23
```
=> GPU на ПК1 работает: large-v3 на CUDA грузится ~8 с, распознавание ~1 с, язык ru.
(кэш модели large-v3 скачан с HF в первый раз: ~3.3 ГБ).

Гуй smoke-тест (запуск whisper-local.exe, трей):
- старт чистый, без CUDA/cuBLAS-ошибок; user_settings.yaml применился;
- hotkey зарегистрированы: recording ctrl+space, stop f8, всего 9;
- модель large-v3 запрошена с HF; девайс LifeCam VX-2000; 21 voice command; 6 transforms;
- приложение живо в трее.

## Git push
- (заполнится по факту в шаге 6 — ниже в этом же сеансе.)

## Проблемы / замечания
- Machine PATH (PhysX\Common cudart 6.5) остался нечищенным из-за прав UAC; не влияет на
  работу, т.к. CT2 берёт CUDA-12 DLL локально из ctranslate2\. Оставить как запасной вопрос:
  при желании почистить вручную (удалить PhysX\Common из системных переменных с правами
  администратора).
- Живая диктовка микрофоном (Блокнот -> Ctrl+Space) требует пользователя; движок и запуск
  GUI проверены §16-прогоном + smoke-тестом. Финальный голосовой тест — на стороне владельца.
- Первая загрузка large-v3 заняла время (скачивание с HF); повторный запуск — мгновенный (кэш).
