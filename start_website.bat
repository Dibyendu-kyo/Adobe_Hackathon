@echo off
echo.
echo ========================================
echo 🌐 Adobe Hackathon Website Launcher
echo ========================================
echo.
echo ✅ Login button removed - Direct access
echo ✅ Your Python code integrated
echo ✅ Professional web interface ready
echo.

echo Checking prerequisites...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found! Please install Python 3.9+
    pause
    exit /b 1
)

node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not found! Please install Node.js 18+
    pause
    exit /b 1
)

echo Installing dependencies...
pip install -r requirements.txt >nul 2>&1

cd adobe-scan-portal
npm install >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Node.js dependencies!
    pause
    exit /b 1
)

echo.
echo Checking AI models...
cd ..
if not exist "models\all-MiniLM-L6-v2" (
    echo Downloading AI models for Round 1B...
    python download_models.py
) else (
    echo ✅ AI models ready
)

echo.
echo ========================================
echo 🚀 Starting Your Website
echo ========================================
echo.
echo Your website will be available at:
echo 👉 http://localhost:3000
echo.
echo Features:
echo ✅ Round 1A: Uses your pdf_extractor_generic.py
echo ✅ Round 1B: Uses your semantic ranking & chunking
echo ✅ No login required - Direct access
echo ✅ Professional UI with real-time processing
echo.
echo Press Ctrl+C to stop the server
echo.

cd adobe-scan-portal
npm run dev