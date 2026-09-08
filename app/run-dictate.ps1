# run-dictate.ps1 -- launch the thin dictation script in the SAME Python where
# the direct faster-whisper GPU test passed (whisper-local bundled interpreter,
# with cuBLAS DLLs next to ctranslate2). Run via pwsh.
#
# Usage:
#   pwsh -File .\app\run-dictate.ps1                 # GPU defaults (large-v3, cuda, float16, ru)
#   pwsh -File .\app\run-dictate.ps1 --device cpu --compute-type int8 --model small
#   $env:DICTATE_PYTHON = 'C:\path\to\python.exe'; pwsh -File .\app\run-dictate.ps1   # override interpreter
#
# All extra args are passed straight through to dictate.py.

$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$script = Join-Path $here 'dictate.py'

# Interpreter: env override wins; otherwise the whisper-local bundled Python.
$py = $env:DICTATE_PYTHON
if (-not $py) {
    $py = Join-Path $env:LOCALAPPDATA 'Python\pythoncore-3.14-64\python.exe'
}
if (-not (Test-Path $py)) {
    Write-Error "Python not found: $py  (set DICTATE_PYTHON to override)"
    exit 1
}

Write-Host "Using python: $py"
& $py $script @args
exit $LASTEXITCODE
