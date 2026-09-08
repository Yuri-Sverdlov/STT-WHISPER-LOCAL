# TASK — активное задание (архитектор -> кодер)

Статус: активно | Дата: 2026-09-08 | Машина: **ПК1 (RTX 3050)**

## Официально: трек-подход (свой скрипт)
Основной способ офлайн-диктовки в проекте — **свой тонкий скрипт `app/dictate.py`**
(трек A1) поверх faster-whisper, в ОБХОД GUI-обёртки whisper-local (A2, виснет на
«transcribing», проглатывая ошибку cuBLAS). GUI оставлен только как резерв/справка.
Канон: CONTEXT.md («Треки»), AGENTS.md (трек A, грабли), REPORT.md, PROJECT_LOG.md.

**Незыблемое требование:** скрипт запускать в ТОМ ЖЕ окружении, где прошёл прямой
GPU-тест — bundled Python `%LOCALAPPDATA%\Python\pythoncore-3.14-64` (cuBLAS DLL
рядом с ctranslate2). Среду не переизобретать.

## Железо и пути (зафиксировано архитектором)

| Параметр | ПК1 (эта машина) | ПК2 |
|---|---|---|
| GPU | NVIDIA RTX 3050, **8 ГБ VRAM** | NVIDIA RTX 4060, **8 ГБ VRAM** |
| RAM | **16 ГБ** | **32 ГБ** |
| Клон репо | `G:\_MY-PROGRAMMING_3\STT-WHISPER-LOCAL` | `G:\AI\_MY_PROGRAMMING_3\STT-WHISPER-LOCAL` |
| Remote | `https://github.com/Yuri-Sverdlov/STT-WHISPER-LOCAL` | тот же |
| Ветка | `main` | `main` |

Оба ПК равноправны — «целевой» машины нет.

## Спецификация скрипта (эталон)
- Запись: sounddevice, 16 кГц, моно.
- Модель: faster-whisper `large-v3`, `device=cuda`, `compute_type=float16`, `language=ru`.
- Модель грузить и вызывать в ОДНОМ выделенном потоке через очередь — не из callback хоткея.
- Хоткей: **hold-to-record** `ctrl+space` (зажать — запись, отпустить -> транскрайб ->
  вставка). Выход — `ctrl+shift+q`. Только буквы/space/F-клавиши/модификаторы; **не**
  правый Alt/AltGr и **не** символы (библиотека их теряет). Альт-режимы: `--toggle`
  (тап/тап, лучше на одиночной клавише f9), `--stop-key f8` (двухклавишный).
  ВАЖНО: тумблер на зажатом модификаторе хрупок — автоповтор Windows рвёт запись
  на куски; hold-to-record этого лишён (start идемпотентен, стоп — по отпусканию).
- Вставка: через буфер обмена (pyperclip) + эмуляция Ctrl+V — надёжно для кириллицы.
- Все параметры — CLI с дефолтами; фолбэк GPU->CPU: `--device cpu --compute-type int8 --model small`.

## Статус по машинам
- **ПК1:** ГОТОВО и подтверждено живой диктовкой (2026-09-08). `app/dictate.py` на GPU
  (large-v3, init ~5-8 c, transcribe ~1.5 c, ru); hold-to-record `ctrl+space`, вставка
  Ctrl+V в Блокнот работает (диктовка ~10 c -> 100 символов, peak ~0.18).
- **ПК2:** паритет — запустить тот же `app/dictate.py` в его окружении (где уже работает
  GUI на GPU), проверить живой диктовкой. При OOM на 8 ГБ — фолбэк medium/CPU.

## Следующие шаги
1. ПК2: развернуть и проверить `app/dictate.py` (git pull -> запуск -> живой тест).
2. (Опц.) Автозапуск/трей, чтобы не держать консоль. По желанию владельца.
3. Трек B (Gemini) — только после стабильности A1 на обоих ПК.

## Не делать
- Не переизобретать окружение Python (только bundled `pythoncore-3.14-64` с cuBLAS).
- Ничего не удалять по своей инициативе (DEV-NOTES §13.2).
- Не коммитить секреты, `user_settings.yaml`, `.env`, веса моделей.
- CUDA Toolkit с сайта NVIDIA не качать и не ставить (драйвер даёт runtime CUDA 12+).

## Git (по явному git-заданию, Windows-side)
```powershell
cd G:\_MY-PROGRAMMING_3\STT-WHISPER-LOCAL
git status; git diff
gh repo view --json visibility
git add app/ tasks/TASK.md tasks/REPORT.md CONTEXT.md PROJECT_LOG.md
git commit -m "<осмысленное сообщение>"
git push origin main
git ls-remote origin refs/heads/main
```
