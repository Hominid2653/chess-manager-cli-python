@echo off
setlocal
cd /d "%~dp0"

if exist "%~dp0venv\Scripts\python.exe" (
    "%~dp0venv\Scripts\python.exe" "%~dp0main.py" %*
) else (
    python "%~dp0main.py" %*
)
