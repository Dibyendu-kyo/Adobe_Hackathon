@echo off
REM Adobe Hackathon PDF Processing - Docker Deployment Script for Windows

echo 🚀 Starting Adobe PDF Processing App Deployment...

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker Compose is not installed. Please install Docker Compose first.
    pause
    exit /b 1
)

echo [INFO] Creating necessary directories...
if not exist "models" mkdir models
if not exist "ssl" mkdir ssl
if not exist "logs" mkdir logs

REM Download models if they don't exist
if not exist "models\all-MiniLM-L6-v2" (
    echo [INFO] Downloading AI models...
    python download_models.py
    if %errorlevel% neq 0 (
        echo [WARNING] Model download failed, continuing anyway...
    )
)

echo [INFO] Building Docker images...
docker-compose build --no-cache
if %errorlevel% neq 0 (
    echo [ERROR] Docker build failed!
    pause
    exit /b 1
)

echo [INFO] Starting the application...
docker-compose up -d
if %errorlevel% neq 0 (
    echo [ERROR] Failed to start the application!
    pause
    exit /b 1
)

echo [INFO] Waiting for application to start...
timeout /t 30 /nobreak >nul

echo [INFO] Checking application health...
curl -f http://localhost:3000/api/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Application is running successfully!
    echo 🎉 Adobe PDF Processing App is now available at:
    echo    📱 Frontend: http://localhost:3000
    echo    🔍 Health Check: http://localhost:3000/api/health
    echo.
    echo [INFO] To view logs: docker-compose logs -f
    echo [INFO] To stop: docker-compose down
    echo [INFO] To restart: docker-compose restart
) else (
    echo [ERROR] Application health check failed!
    echo [INFO] Checking logs...
    docker-compose logs --tail=50
    pause
    exit /b 1
)

echo [INFO] Running containers:
docker-compose ps

echo.
echo Press any key to continue...
pause >nul