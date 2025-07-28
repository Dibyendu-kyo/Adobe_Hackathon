@echo off
echo 🏆 Adobe Hackathon - Docker Submission Script

echo.
echo ========================================
echo Building Round 1A Docker Container
echo ========================================
cd round1a
docker build --platform linux/amd64 -t round1a:submission .
if %errorlevel% neq 0 (
    echo [ERROR] Round 1A build failed!
    pause
    exit /b 1
)

echo.
echo Testing Round 1A with sample PDF...
if not exist input mkdir input
if not exist output mkdir output
copy ..\sample.pdf input\
docker run --rm -v %cd%\input:/app/input -v %cd%\output:/app/output --network none round1a:submission
if %errorlevel% neq 0 (
    echo [ERROR] Round 1A test failed!
    pause
    exit /b 1
)

echo [SUCCESS] Round 1A container ready for submission!
cd ..

echo.
echo ========================================
echo Downloading Models for Round 1B
echo ========================================
python download_models.py
if %errorlevel% neq 0 (
    echo [WARNING] Model download failed, continuing...
)

echo.
echo ========================================
echo Building Round 1B Docker Container
echo ========================================
cd round1b
docker build --platform linux/amd64 -t round1b:submission .
if %errorlevel% neq 0 (
    echo [ERROR] Round 1B build failed!
    pause
    exit /b 1
)

echo.
echo Testing Round 1B with sample PDFs...
if not exist input mkdir input
if not exist output mkdir output
copy ..\sample.pdf input\
copy ..\sample1.pdf input\
docker run --rm -v %cd%\input:/app/input -v %cd%\output:/app/output -v %cd%\..\models:/app/models --network none round1b:submission
if %errorlevel% neq 0 (
    echo [ERROR] Round 1B test failed!
    pause
    exit /b 1
)

echo [SUCCESS] Round 1B container ready for submission!
cd ..

echo.
echo ========================================
echo 🎉 Docker Submission Ready!
echo ========================================
echo.
echo Round 1A Container: round1a:submission
echo Round 1B Container: round1b:submission
echo.
echo Submission Commands:
echo   Round 1A: docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none round1a:submission
echo   Round 1B: docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output -v $(pwd)/models:/app/models --network none round1b:submission
echo.
echo Next: Deploy web interface to Vercel
echo   cd adobe-scan-portal
echo   vercel --prod
echo.
pause