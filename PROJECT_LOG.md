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

## 2026-09-07 — GitHub и перенос на RTX 4060
- Репозиторий на GitHub: `Yuri-Sverdlov/STT-WHISPER-LOCAL`, ветка `main`.
- Клон на целевой машине RTX 4060: `G:\AI\_MY_PROGRAMMING_3\STT-WHISPER-LOCAL`.
- HEAD `2a08f8d` — docs: drop absolute DEV-NOTES path from redirects.
## 2026-09-07 — Пересмотр: CUDA Toolkit не нужен
- Консультант + сверка с docs/gpu-setup.md whisper-local: GPU-библиотеки **не в .exe**,
  ставятся через pip при onboarding (`nvidia-*-cu12`). CUDA Toolkit (Option B) отменён.
- Драйвер 581.57 / CUDA 13.0 на RTX 4060 достаточен. TASK rev.2: скачать whisper-local
  (браузер/winget), принять GPU setup, далее large-v3 + тест.
- Кодер застрял в browser-цикле на NVIDIA download pages — явный запрет в TASK.

## 2026-09-07 — Трек A заработал на GPU (RTX 4060). Разбор граблей
Разложено Claude (консультант, через Desktop Commander) по просьбе Юрия — без агентов Cursor.

Отчёт кодера останавливался на «GPU ready, тест ждёт пользователя». Но «модель грузится»
НЕ значит «распознаёт»: реальная диктовка падала/висла. Причины (все устранены):

1. `recording_hotkey: AltGr+/` — библиотека global_hotkeys не знает ключ `altgr` -> краш
   при старте. Правый Alt / AltGr использовать НЕЛЬЗЯ.
2. Символ `/` как клавиша не переживает нормализацию whisper_key (становится пустым ключом)
   -> краш. Годятся только буквы, `space`, F-клавиши, модификаторы.
3. Пустой `stop_key: ''` — БАГ whisper-local 0.18.3: добавляется в привязки без проверки
   на пустоту -> "key []" -> краш при старте. Лечение: задать валидную клавишу (`f8`).
4. ГЛАВНОЕ — нет cuBLAS. Сборка ctranslate2 несёт cudnn64_9.dll, но НЕ несёт
   cublas64_12.dll. Модель грузится, но первый расчёт (encode) бросает
   "Library cublas64_12.dll is not found" — приложение ошибку ПРОГЛАТЫВАЕТ и виснет на
   "transcribing...". В UI ошибки не видно; вскрыто прямым прогоном faster_whisper через
   venv-python.

Фиксы:
- `user_settings.yaml` (пер-машинный): `recording_hotkey: ctrl+space` (hold-to-record),
  `stop_key: f8`.
- `pip install nvidia-cublas-cu12` в venv приложения + СКОПИРОВАНЫ cublas64_12.dll и
  cublasLt64_12.dll из `...\site-packages\nvidia\cublas\bin` в `...\site-packages\ctranslate2`
  (CT2 ищет DLL только в своей папке, рядом с cudnn64_9.dll). Один pip без копии не помогает.

Проверка: прямой прогон faster_whisper на GPU — model load 3.3s, transcribe 0.7s (float16).
Юрий подтвердил вживую: Ctrl+Space -> русский текст вставляется в Блокнот. Трек A на GPU ЗАКРЫТ.

## 2026-09-08 — Две равноправные машины; задание для ПК1
- Уточнение от Юрия: нет «целевой» машины; проект на двух ПК (3050/16 ГБ и 4060/32 ГБ),
  оба должны работать стабильно.
- ПК1 (RTX 3050): `git pull` с GitHub (канон с ПК2 уже в origin/main).
- Архитектор обновил CONTEXT.md, TASK.md (развёртывание трек A на ПК1 + git push),
  сбросил REPORT.md. Push — задача кодера на ПК1.

## 2026-09-08 — Трек A на ПК1 (RTX 3050): GPU включён, large-v3 на CUDA
- Sync: HEAD == origin/main == 05f1dfe; рабочие правки канона (архитектор) — в коммит шага 6.
- Диагностика CUDA: найден виновник mismatch — PhysX\Common\cudart64_65.dll (CUDA 6.5) в PATH.
  User-PATH очищен (запись удалена); Machine-PATH — нет прав без UAC, НЕ тронут (не помешал).
- cuBLAS установлен в pythoncore-3.14-64: nvidia-cublas-cu12 + nvidia-cuda-runtime-cu12;
  cublas64_12.dll/cublasLt64_12.dll/cudart64_12.dll скопированы в ctranslate2\ (рядом с cudnn64_9).
- Конфиг (пер-машинный): профиль dictation -> large-v3/cuda/float16/ru, ctrl+space/f8; бэкапы *.bak-20260908.
- Проверка запуском (§16): faster_whisper large-v3 cuda float16 — init 7.87c, transcribe 1.09c, lang=ru.
  GUI smoke-тест: старт чистый, без CUDA-ошибок, хоткеи 9, large-v3 с HF, приложение живо в трее.
- Репо не пушился в этой записи — ждёт шага 6 (git-задание) в этом же сеансе.

## 2026-09-08 — Своя тонкая диктовка (трек-подход, ПК1)
- По прямому заданию Юрия: минимальный скрипт диктовки на faster-whisper в обход
  GUI whisper-local (она виснет, проглатывая ошибку cuBLAS). Осознанный «трек-подход».
- Окружение — то же bundled Python `pythoncore-3.14-64`, где прошёл прямой GPU-тест
  (cuBLAS рядом с ctranslate2). Среда не переизобреталась.
- Создан `app/`: `dictate.py` (sounddevice 16 кГц моно -> faster-whisper
  large-v3/cuda/float16/ru -> буфер+Ctrl+V), `run-dictate.ps1` (лаунчер без хардкода
  путей), `README.md`. Модель — в одном выделенном потоке через очередь, не из callback.
- Хоткеи: Ctrl+Space старт / F8 стоп+транскрайб+вставка / Ctrl+Shift+Q выход
  (библиотека `keyboard`; только буквы/space/F/модификаторы — грабля AltGr/символов обойдена).
- Доустановлены в окружение: sounddevice 0.5.6, pyperclip 1.11.0, keyboard 0.13.5.
- Проверка запуском (§16, headless): py_compile OK; `transcribe_worker` на GPU
  init=7.03s / transcribe=0.96s / lang=ru, БЕЗ зависания на cuBLAS; микрофон 16 кГц
  открылся/закрылся; хоткеи регистрируются без админа. Живой голосовой тест — за владельцем.
