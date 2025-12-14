@echo off
REM ========================================
REM PDSA Eight Queens - Simple Start Script
REM ========================================
REM Double-click this file to start the game!

echo.
echo ========================================
echo   PDSA Eight Queens Game - Starting...
echo ========================================
echo.

cd /d "%~dp0"

REM Activate virtual environment and start server
call .venv\Scripts\activate.bat
python -m uvicorn shared.backend.main:app --reload --host 127.0.0.1 --port 8000

pause
