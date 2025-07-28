@echo off
echo 🌐 Adobe Hackathon - Vercel Deployment Script

echo.
echo ========================================
echo Preparing Vercel Deployment
echo ========================================

cd adobe-scan-portal

echo Checking Node.js dependencies...
npm install
if %errorlevel% neq 0 (
    echo [ERROR] npm install failed!
    pause
    exit /b 1
)

echo.
echo Building Next.js application...
npm run build
if %errorlevel% neq 0 (
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Deploying to Vercel
echo ========================================

echo.
echo Please ensure you have:
echo 1. Vercel CLI installed: npm install -g vercel
echo 2. Logged in to Vercel: vercel login
echo.

echo Deploying to production...
vercel --prod
if %errorlevel% neq 0 (
    echo [ERROR] Vercel deployment failed!
    echo.
    echo Troubleshooting:
    echo 1. Install Vercel CLI: npm install -g vercel
    echo 2. Login to Vercel: vercel login
    echo 3. Try again: vercel --prod
    pause
    exit /b 1
)

echo.
echo ========================================
echo 🎉 Vercel Deployment Complete!
echo ========================================
echo.
echo Your Adobe Hackathon web interface is now live!
echo.
echo Features deployed:
echo ✅ Round 1A: Document Structure Extraction
echo ✅ Round 1B: Persona-Driven Intelligence
echo ✅ Professional UI with real-time processing
echo ✅ Constraint validation and monitoring
echo ✅ File management and results display
echo.
echo Ready for hackathon demonstration! 🏆
echo.
pause