@echo off
echo ==============================================
echo Round 1A: Document Structure Extraction Test
echo ==============================================

echo 1. Testing Python implementation...
python test.py

echo.
echo 2. Building Docker container...
docker build -t round1a .

echo.
echo 3. Creating input and output directories...
if not exist input mkdir input
if not exist output mkdir output

echo.
echo 4. Copying sample PDF to input directory...
if exist "..\sample.pdf" (
    copy "..\sample.pdf" input\
) else if exist "..\sample1.pdf" (
    copy "..\sample1.pdf" input\
) else if exist "..\South of France - Cities.pdf" (
    copy "..\South of France - Cities.pdf" input\
) else (
    echo ❌ No sample PDF found. Please ensure sample PDFs are in parent directory.
    pause
    exit /b 1
)

echo.
echo 5. Running Docker container...
docker run --rm -v "%cd%\input:/app/input" -v "%cd%\output:/app/output" round1a

echo.
echo 6. Results:
if exist "output\document_structure.json" (
    echo ✅ Docker test successful!
    echo 📄 Results saved to output\document_structure.json
    echo.
    echo Contents:
    type output\document_structure.json
) else (
    echo ❌ Docker test failed - no output file generated
)

pause