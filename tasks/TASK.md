# TASK — активное задание (архитектор -> кодер)

Статус: активно | Дата: 2026-09-08 | Машина: **ПК1 (RTX 3050)**

## Цель
Синхронизировать репозиторий с GitHub и развернуть трек A (whisper-local) на **ПК1**
так, чтобы диктовка была стабильной, как на ПК2.

## Железо и пути (зафиксировано архитектором)

| Параметр | ПК1 (эта машина) | ПК2 (уже работает) |
|---|---|---|
| GPU | NVIDIA RTX 3050, **8 ГБ VRAM** | NVIDIA RTX 4060, **8 ГБ VRAM** |
| RAM | **16 ГБ** | **32 ГБ** |
| Клон репо | `G:\_MY-PROGRAMMING_3\STT-WHISPER-LOCAL` | `G:\AI\_MY_PROGRAMMING_3\STT-WHISPER-LOCAL` |
| Remote | `https://github.com/Yuri-Sverdlov/STT-WHISPER-LOCAL` | тот же |
| Ветка | `main` | `main` |

Отдельной «целевой машины» нет — оба ПК равноправны.

## Предыстория
- ПК2: трек A на GPU закрыт (large-v3, cuda, float16, ru, ctrl+space) — см. REPORT.md,
  PROJECT_LOG 2026-09-07, AGENTS.md.
- ПК1: ранее работал CPU-базлайн (base, int8, Ctrl+Win). Канон на GitHub обновлён с ПК2.
- Архитектор обновил CONTEXT.md и это задание; push — задача кодера (ниже).

## Шаги

### 1. Sync с GitHub
```powershell
cd G:\_MY-PROGRAMMING_3\STT-WHISPER-LOCAL
git fetch origin
git status
git pull origin main
git rev-parse HEAD
git rev-parse origin/main
```
HEAD и origin/main должны совпасть. Если pull ругается на untracked — DEV-NOTES §7
(backup в `.backup_local/`, не коммитить).

### 2. Установка whisper-local на ПК1
- Скачать v0.18.3 (GitHub releases или winget). SHA256:
  `56cef2b71416fce31f69f3bec4d21d9a7a4f1fc93e383c4ca568a7701a7037fa`.
- При onboarding **принять GPU setup** (pip nvidia-*-cu12). CUDA Toolkit НЕ ставить.
- Если mismatch «found CUDA 6.5» — найти и показать в отчёте старый cudart в PATH
  (часто `PhysX\Common` в Machine PATH), только потом править. См. AGENTS.md.

### 3. Конфиг `%APPDATA%\whisperkey\user_settings.yaml` (пер-машинный)

**Целевой профиль ПК1 (GPU, как на ПК2):**
```yaml
whisper:  { model: large-v3, device: cuda, compute_type: float16, language: ru }
hotkey:   { recording_hotkey: ctrl+space, stop_key: f8 }
```
- Хоткеи: только буквы/space/F-клавиши; **не** AltGr, **не** символы (`/` и т.п.).
- **cuBLAS обязателен:** `pip install nvidia-cublas-cu12` + копия `cublas64_12.dll` и
  `cublasLt64_12.dll` в `...\site-packages\ctranslate2\` — см. AGENTS.md.

**Fallback, если GPU не заводится или OOM на 8 ГБ VRAM / 16 ГБ RAM:**
```yaml
whisper:  { model: medium, device: cuda, compute_type: float16, language: ru }
```
или CPU:
```yaml
whisper:  { model: small, device: cpu, compute_type: int8, language: ru }
```
Выбранный профиль и причину — в REPORT.md.

### 4. Тест (DEV-NOTES §16)
- Блокнот -> зажать **Ctrl+Space** -> русская фраза (напр. «Привет, как дела?»).
- Зафиксировать: время распознавания, модель, device, вставка текста.
- При сбое — прямой прогон faster_whisper через venv-python (не полагаться на GUI).

### 5. REPORT.md
Заполнить по фактическому запуску: диагностика CUDA/PATH, конфиг, cuBLAS, тест, fallback.

### 6. Git commit + push (явное задание)
```powershell
cd G:\_MY-PROGRAMMING_3\STT-WHISPER-LOCAL
git status
git diff
gh repo view --json visibility
git add CONTEXT.md tasks/TASK.md tasks/REPORT.md
git commit -m "docs: two-PC setup; track A deploy task for RTX 3050 (PC1)"
git push origin main
git ls-remote origin refs/heads/main
```
Коммитить только канон (docs). Конфиг whisper-local и `.env` — **не** в git.
Если архитектор уже закоммитил часть правок локально — добавить в commit только новое.

## Не делать
- Ничего не удалять по своей инициативе (DEV-NOTES §13.2).
- Не коммитить секреты, `user_settings.yaml`, `.env`.
- CUDA Toolkit с сайта NVIDIA не качать и не ставить.
