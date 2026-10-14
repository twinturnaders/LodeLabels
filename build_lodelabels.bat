@echo off
setlocal EnableExtensions
cd /d "%~dp0"

title LodeLabels Builder

echo.
echo ============================================================
echo                 LodeLabels Windows Builder
echo ============================================================
echo.

REM ------------------------------------------------------------
REM Make sure the virtual environment exists.
REM ------------------------------------------------------------

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] .venv was not found.
    echo.
    echo Run your install setup first, or create it with:
    echo     python -m venv .venv
    echo.
    pause
    exit /b 1
)

set "PYTHON=.venv\Scripts\python.exe"

REM ------------------------------------------------------------
REM Make sure PyInstaller is available in the project venv.
REM ------------------------------------------------------------

echo [1/4] Checking PyInstaller...

"%PYTHON%" -m PyInstaller --version >nul 2>&1

if errorlevel 1 (
    echo PyInstaller is not installed. Installing it now...
    "%PYTHON%" -m pip install --upgrade pyinstaller

    if errorlevel 1 (
        echo.
        echo [ERROR] PyInstaller installation failed.
        pause
        exit /b 1
    )
)

REM ------------------------------------------------------------
REM Clean old build output.
REM ------------------------------------------------------------

echo [2/4] Cleaning old build files...

if exist "build" rmdir /s /q "build"
if exist "dist\LodeLabels" rmdir /s /q "dist\LodeLabels"
if exist "LodeLabels.spec" del /q "LodeLabels.spec"

REM ------------------------------------------------------------
REM Build the app.
REM
REM Default PyInstaller mode is ONE-FOLDER, which is much easier
REM to debug and more reliable for PySide6 than one-file mode.
REM ------------------------------------------------------------

echo [3/4] Building LodeLabels...

"%PYTHON%" -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --windowed ^
    --name "LodeLabels" ^
    --hidden-import win32ui ^
    --hidden-import win32print ^
    --hidden-import pywintypes ^
    --hidden-import win32timezone ^
    --hidden-import PIL.ImageWin ^
    gui_app.py

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed.
    echo Scroll up to see the PyInstaller error.
    pause
    exit /b 1
)

REM ------------------------------------------------------------
REM Keep the Chrome extension visible beside the EXE so it can
REM still be loaded as an unpacked extension in Chrome.
REM ------------------------------------------------------------

echo [4/4] Copying Chrome extension...

if exist "chrome-extension" (
    xcopy /e /i /y "chrome-extension" "dist\LodeLabels\chrome-extension" >nul
) else (
    echo [WARNING] chrome-extension folder was not found.
    echo Auto-detection will still require the extension separately.
)

REM Add a small launcher that guarantees the working directory is
REM the LodeLabels folder. This keeps data, labels, and sessions
REM beside the packaged application with the current codebase.

(
echo @echo off
echo cd /d "%%~dp0"
echo start "" "LodeLabels.exe"
) > "dist\LodeLabels\Run LodeLabels.bat"

echo.
echo ============================================================
echo BUILD COMPLETE
echo ============================================================
echo.
echo Your packaged app is here:
echo.
echo     dist\LodeLabels\LodeLabels.exe
echo.
echo The entire dist\LodeLabels folder is the distributable app.
echo Do NOT send only the EXE -- keep the whole folder together.
echo.
echo For your own use, you can double-click:
echo.
echo     dist\LodeLabels\Run LodeLabels.bat
echo.
echo or LodeLabels.exe directly.
echo.
pause
