# PROJECT_LOG — STT-WHISPER-LOCAL

Append-only журнал сессий. Новые записи — снизу.

## 2026-09-06 — Инициализация проекта
- Создан канонический комплект по DEV-NOTES §1: AGENTS.md, CONTEXT.md, CLAUDE.md,
  PROJECT_LOG.md, tasks/{TASK,REPORT}.md, tasks/done/, README.md, .gitignore.
- Стратегия: трек A (whisper-local, офлайн) + трек B (Gemini 3.5 Transcribe, Live API).
- whisper-local: лаунчер 0.18.3 скачан в Downloads, sha256 сверён
  (56cef2b71416fce31f69f3bec4d21d9a7a4f1fc93e383c4ca568a7701a7037fa), запущен.
- Установщик обнаружил GPU RTX 3050; CUDA mismatch (found 6.5 / requires 12) ->
  решено стартовать трек A на CPU, GPU отложить.
- git ещё не инициализирован (по §3 — задача кодера на Windows).

## 2026-09-06 — Трек A запущен на CPU, проект переименован
- Папка переименована TTS-WHISPER-LOCAL -> STT-WHISPER-LOCAL, имена в файлах поправлены
  (домен проекта — STT, распознавание речи).
- whisper-local: выбран режим [2] (CPU). Модель base, int8. Значок в трее, хоткей Ctrl+WIN,
  авто-вставка CTRL+V.
- Проверено запуском (RTX 3050): "Привет, как дела?" -> ~1.0-1.1 c, вставка в Блокнот работает;
  русский на base распознаётся без настройки языка.
- Уточнено железо: RTX 3050 — машина первичного теста; проект продолжается на машине RTX 4060.
- Активная задача переключена на развёртывание на RTX 4060 + GPU (CUDA 12).
