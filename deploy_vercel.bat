@echo off
echo 🌐 Quick Vercel Deployment for Adobe Hackathon Website
echo =====================================================

echo.
echo 🔧 Step 1: Preparing for Vercel Deployment
echo =====================================================

echo Checking Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is required. Please install Node.js 18+ and try again.
    pause
    exit /b 1
)

echo Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is required. Please install Python 3.9+ and try again.
    pause
    exit /b 1
)

echo.
echo 📦 Step 2: Installing Dependencies
echo =====================================================

echo Installing Python dependencies...
pip install -r requirements.txt

echo Installing Node.js dependencies...
cd adobe-scan-portal
npm install

echo.
echo 🤖 Step 3: Downloading AI Models
echo =====================================================
cd ..
if not exist "models\all-MiniLM-L6-v2" (
    echo Downloading AI models for Round 1B...
    python download_models.py
) else (
    echo AI models already exist.
)

echo.
echo 🏗️ Step 4: Building Production Version
echo =====================================================
cd adobe-scan-portal
echo Building Next.js application...
npm run build
if %errorlevel% neq 0 (
    echo [ERROR] Build failed. Please check for errors above.
    pause
    exit /b 1
)

echo.
echo ☁️ Step 5: Installing Vercel CLI
echo =====================================================
echo Installing Vercel CLI globally...
npm install -g vercel

echo.
echo 🚀 Step 6: Deploying to Vercel
echo =====================================================
echo.
echo 🎯 IMPORTANT: Follow these steps during deployment:
echo.
echo 1. When prompted "Set up and deploy", choose: Y (Yes)
echo 2. When asked "Which scope", choose your account
echo 3. When asked "Link to existing project", choose: N (No)
echo 4. When asked "What's your project's name", press Enter (use default)
echo 5. When asked "In which directory", press Enter (use current)
echo 6. When asked "Want to override settings", choose: N (No)
echo.
echo Starting deployment...
echo.

vercel --prod

if %errorlevel% equ 0 (
    echo.
    echo ✅ SUCCESS! Your website has been deployed!
    echo.
    echo 🌐 Your website is now live and accessible worldwide!
    echo 📱 Anyone can access it from any device, anywhere!
    echo 🔗 The URL has been displayed above - share it with anyone!
    echo.
    echo 🎯 Features available on your live website:
    echo   ✅ Round 1A: Document Structure Extraction
    echo   ✅ Round 1B: Persona-Driven Intelligence  
    echo   ✅ Professional UI with real-time processing
    echo   ✅ Mobile-friendly design
    echo   ✅ No login required - instant access
    echo.
    echo 🏆 Your Adobe Hackathon solution is now universally accessible!
) else (
    echo.
    echo ❌ Deployment failed. Common solutions:
    echo.
    echo 1. Make sure you have a Vercel account (free at vercel.com)
    echo 2. Check your internet connection
    echo 3. Try running: vercel login
    echo 4. Then run this script again
    echo.
    echo For help, visit: https://vercel.com/docs
)

echo.
pause