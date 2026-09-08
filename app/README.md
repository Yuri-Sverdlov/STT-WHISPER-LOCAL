# app/ — тонкая диктовка на faster-whisper (трек-подход)

Свой минимальный скрипт голосового ввода в обход GUI-обёртки whisper-local
(она проглатывает ошибку cuBLAS и виснет на «transcribing»). Скрипт запускается
в **том же** Python, где прошёл прямой GPU-тест — встроенный интерпретатор
whisper-local `%LOCALAPPDATA%\Python\pythoncore-3.14-64`, куда рядом с
`ctranslate2` скопированы cuBLAS DLL (см. AGENTS.md, трек A).

## Файлы
- `dictate.py` — сам скрипт (запись микрофона → faster-whisper → вставка).
- `run-dictate.ps1` — лаунчер: находит нужный python, пробрасывает аргументы.

## Запуск
```powershell
cd G:\_MY-PROGRAMMING_3\STT-WHISPER-LOCAL
pwsh -File .\app\run-dictate.ps1
```

## Хоткеи
- **Ctrl+Space** — тумблер: первое нажатие — старт записи, второе — стоп → транскрайб →
  вставка под курсор (через буфер + эмуляция Ctrl+V).
- **Ctrl+Shift+Q** — выход (или Ctrl+C в консоли).

Перед вставкой сфокусируй целевое окно (например, Блокнот).

Двухклавишный режим (отдельный стоп), если нужен:
```powershell
pwsh -File .\app\run-dictate.ps1 --stop-key f8
```

## Дефолты и фолбэк
Дефолт — GPU-эталон ПК2: `large-v3 / cuda / float16 / ru`.
Всё меняется CLI-аргументами (абсолютных путей в коде нет):
```powershell
# CPU-фолбэк при проблемах с GPU / нехватке VRAM
pwsh -File .\app\run-dictate.ps1 --device cpu --compute-type int8 --model small
# только копировать в буфер, без авто-Ctrl+V
pwsh -File .\app\run-dictate.ps1 --no-paste
```
`run-dictate.ps1 --help` эквивалент `dictate.py --help` — полный список опций.

## Зависимости (в bundled Python)
`faster-whisper`, `ctranslate2` (+cuBLAS) — уже стоят; для скрипта доустановлены
`sounddevice`, `pyperclip`, `keyboard`.

## Замечания
- Библиотека хоткеев разбирает буквы/`space`/F-клавиши/модификаторы; правый
  Alt/AltGr и символьные клавиши использовать нельзя (грабля из устава).
- Скрипт и его зависимости — не веса моделей; в git входит только код `app/`.
