@echo off
echo ========================================
echo Adobe Hackathon Web Interface Launcher
echo ========================================

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo ✅ Python found

echo.
echo Starting web interface...
python run_web.py

pause