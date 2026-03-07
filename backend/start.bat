@echo off
echo Starting WebMedic Backend Server...
echo.
echo Press Ctrl+C once to stop the server
echo.

cd /d "%~dp0"
call venv\Scripts\activate.bat
python run.py

echo.
echo Server stopped.
pause
