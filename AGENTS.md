# AGENTS.md — устав кодера (STT-WHISPER-LOCAL)

> Общие правила среды — в файле DEV-NOTES.md (путь на этой машине даёт Юрий в начале сессии; на разных ПК он различается). Здесь только проектное;
> канон не дублируем, а ссылаемся на пункты.

## Старт сессии (терминал)
Прочитать `CONTEXT.md` -> `AGENTS.md` -> `tasks/TASK.md`, выполнить задание,
заполнить `tasks/REPORT.md`.

## Правила
- **Правда о состоянии** — только в `REPORT.md` (что сейчас) и `PROJECT_LOG.md`
  (что было). Никаких параллельных STATUS/NOTES/NEXT (DEV-NOTES §1).
- **Пути в скриптах** — от `HERE = Path(__file__).resolve().parent`; внешний путь —
  CLI-параметр со значением по умолчанию, не константа. Абсолютные пути запрещены
  (DEV-NOTES §14.1).
- **Кодировка**: в `print()` только ASCII (`->`, `<=`); файлы всегда UTF-8
  (DEV-NOTES §4, §12). `.ps1` запускать через `pwsh`; в PowerShell команды
  разделять `;`, не `&&` (DEV-NOTES §5).
- **Удаление** — только по явному пункту `TASK.md` и только после показа целей
  (`ls` / `--dry-run`). Вне папки проекта — запрещено (DEV-NOTES §13.2).
- **git commit/push** — только кодер на Windows и только по явному git-заданию
  (DEV-NOTES §3). Приватность репозитория проверить ДО первого push
  (`gh repo view --json visibility`); pre-push guard, если появится личное (§3.1).
- **Секреты** (Gemini API key) — в `app/.env`, НЕ коммитить. Комментарии в
  `.env`/`.env.example` — только ASCII (DEV-NOTES §10.4).
- **Проверка** — запуском и сверкой с файлами, а не чтением отчёта (DEV-NOTES §16).
  Инструмент печатает объём проделанной работы, а не только ошибки.

## Трек A — whisper-local (GPU работает на RTX 4060)
- Установщик: `%USERPROFILE%\Downloads\whisper-local.exe` (v0.18.3, sha256
  `56cef2b71416fce31f69f3bec4d21d9a7a4f1fc93e383c4ca568a7701a7037fa`; `.sha256` в релизе
  нет). Конфиг `%APPDATA%\whisperkey\user_settings.yaml` — пер-машинный, в репо не входит.
- GPU: CUDA Toolkit НЕ ставить (драйвер даёт runtime CUDA 12+). Если mismatch «found 6.5» —
  убрать `PhysX\Common` из PATH (проверять и User, и **Machine**), Toolkit не ставить.
- **ГЛАВНАЯ ГРАБЛЯ GPU — нет cuBLAS.** Сборка несёт cuDNN, но не `cublas64_12.dll`. Без него
  распознавание молча виснет на «transcribing…» (ошибка "cublas64_12.dll is not found"
  проглатывается, в UI не видна). Лечение: `pip install nvidia-cublas-cu12` в venv
  приложения, затем СКОПИРОВАТЬ `cublas64_12.dll` и `cublasLt64_12.dll` в
  `...\Lib\site-packages\ctranslate2\` (рядом с `cudnn64_9.dll` — CT2 ищет DLL только там).
- **Хоткеи:** только буквы, `space`, F-клавиши, модификаторы `ctrl/alt/shift/win`.
  НЕЛЬЗЯ: правый Alt/`AltGr` и символы (`/ . ,`) — не разбираются, краш при старте.
  Пустой `stop_key: ''` тоже роняет старт (баг) — задавать любую валидную клавишу.
- Рабочий конфиг: `model large-v3`, `device cuda`, `compute_type float16`, `language ru`;
  `recording_hotkey ctrl+space` (hold-to-record), `stop_key f8`. Диагностика краша —
  запуск exe с перехватом (`& '.\whisper-local.exe' 2>&1`) или прямой прогон faster_whisper
  через venv-python (GUI-окно закрывается за 2-3 с и прячет трейсбек).

## Трек B — Gemini 3.5 Transcribe (позже)
- Python venv; `google-genai`, захват микрофона (`sounddevice`), Live API,
  вставка текста под курсор по хоткею. Команды дублировать под PowerShell 7.
- Ключ — из `app/.env` (`GEMINI_API_KEY`), не хардкодить.
