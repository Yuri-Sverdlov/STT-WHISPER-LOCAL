# AGENTS.md — устав кодера (STT-WHISPER-LOCAL)

> Общие правила среды — в `G:\AI\DEV-NOTES\DEV-NOTES.md`. Здесь только проектное;
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

## Трек A — whisper-local
- Установщик: `%USERPROFILE%\Downloads\whisper-local.exe` (sha256 сверять с
  `.sha256` рядом). Конфиг: `%APPDATA%\whisperkey\user_settings.yaml`.
- GPU не включать до отдельной задачи по CUDA 12 (см. CONTEXT, открытые вопросы).

## Трек B — Gemini 3.5 Transcribe (позже)
- Python venv; `google-genai`, захват микрофона (`sounddevice`), Live API,
  вставка текста под курсор по хоткею. Команды дублировать под PowerShell 7.
- Ключ — из `app/.env` (`GEMINI_API_KEY`), не хардкодить.
