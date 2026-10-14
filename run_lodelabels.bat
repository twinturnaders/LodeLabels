@echo off
setlocal EnableExtensions
cd /d "%~dp0"

REM ============================================================
REM LodeLabels Development Launcher
REM ============================================================

if not exist ".venv\Scripts\python.exe" (
    echo.
    echo [ERROR] LodeLabels virtual environment was not found.
    echo.
    echo Expected:
    echo     .venv\Scripts\python.exe
    echo.
    pause
    exit /b 1
)

echo Starting LodeLabels...
echo.

".venv\Scripts\python.exe" gui_app.py

if errorlevel 1 (
    echo.
    echo LodeLabels exited with an error.
    echo The message above may explain what happened.
    echo.
    pause
)
