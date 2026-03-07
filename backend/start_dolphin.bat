@echo off
chcp 65001 >nul
REM Dolphin ASR Startup Script

echo ========================================
echo    Dolphin ASR Service
echo ========================================
echo.

REM Activate virtual environment
call dolphin_env\Scripts\activate.bat

echo [1/3] Virtual environment activated
echo.

REM Check if FunASR is installed
python -c "import funasr" 2>nul
if errorlevel 1 (
    echo [ERROR] FunASR not installed
    echo Please run: pip install funasr
    pause
    exit /b 1
)

echo [2/3] FunASR installed
echo.

REM Start service
echo [3/3] Starting Dolphin ASR service...
echo Service URL: http://localhost:8888
echo Press Ctrl+C to stop
echo.

python dolphin_server.py

pause
