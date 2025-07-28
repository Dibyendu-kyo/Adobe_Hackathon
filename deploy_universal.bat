@echo off
echo 🌐 Universal Deployment Script for Adobe Hackathon Website
echo ========================================================

echo.
echo 🔧 Step 1: Preparing for Universal Deployment
echo ========================================================

echo Checking prerequisites...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is required for deployment
    pause
    exit /b 1
)

node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is required for deployment
    pause
    exit /b 1
)

echo.
echo 📦 Step 2: Installing Dependencies
echo ========================================================

echo Installing Python dependencies...
pip install -r requirements.txt

echo Installing Node.js dependencies...
cd adobe-scan-portal
npm install

echo.
echo 🤖 Step 3: Downloading AI Models
echo ========================================================
cd ..
if not exist "models\all-MiniLM-L6-v2" (
    echo Downloading AI models...
    python download_models.py
) else (
    echo AI models already exist.
)

echo.
echo 🏗️ Step 4: Building Production Version
echo ========================================================
cd adobe-scan-portal
echo Building Next.js application...
npm run build

echo.
echo 🚀 Step 5: Choose Deployment Method
echo ========================================================
echo.
echo Select your deployment option:
echo 1. Local Network Access (accessible to anyone on your network)
echo 2. Vercel Deployment (free cloud hosting)
echo 3. Railway Deployment (alternative cloud hosting)
echo 4. Docker Deployment (containerized solution)
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto local_network
if "%choice%"=="2" goto vercel
if "%choice%"=="3" goto railway
if "%choice%"=="4" goto docker
echo Invalid choice. Defaulting to local network.

:local_network
echo.
echo 🌐 Starting Local Network Server
echo ========================================================
echo.
echo Your website will be accessible to anyone on your network at:
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4"') do (
    for /f "tokens=1" %%b in ("%%a") do echo   http://%%b:3000
)
echo   http://localhost:3000 (local access)
echo.
echo Press Ctrl+C to stop the server
echo.
npm start -- --hostname 0.0.0.0 --port 3000
goto end

:vercel
echo.
echo ☁️ Deploying to Vercel (Free Cloud Hosting)
echo ========================================================
echo.
echo Installing Vercel CLI...
npm install -g vercel

echo.
echo Deploying to Vercel...
echo Follow the prompts to deploy your website.
echo Your website will get a free .vercel.app URL that anyone can access.
echo.
vercel --prod
goto end

:railway
echo.
echo 🚂 Deploying to Railway (Alternative Cloud Hosting)
echo ========================================================
echo.
echo Installing Railway CLI...
npm install -g @railway/cli

echo.
echo Deploying to Railway...
echo Follow the prompts to deploy your website.
echo Your website will get a free .railway.app URL.
echo.
railway login
railway deploy
goto end

:docker
echo.
echo 🐳 Docker Deployment
echo ========================================================
echo.
echo Building Docker container...
cd ..
docker build -t adobe-hackathon-website .

echo.
echo Starting Docker container...
echo Your website will be accessible at: http://localhost:3000
echo And to anyone on your network at your IP address:3000
echo.
docker run -p 3000:3000 adobe-hackathon-website
goto end

:end
echo.
echo ✅ Deployment process completed!
pause