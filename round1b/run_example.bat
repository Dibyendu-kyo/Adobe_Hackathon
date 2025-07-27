@echo off
echo ==================================================
echo Round 1B: Persona-Driven Document Intelligence Test
echo ==================================================

echo 1. Checking prerequisites...
if not exist "..\models\all-MiniLM-L6-v2" (
    echo ❌ Models not found. Please run 'python download_models.py' from root directory first.
    pause
    exit /b 1
)

echo 2. Testing Python implementation...
python test.py

echo.
echo 3. Building Docker container...
docker build -t round1b .

echo.
echo 4. Creating input, output, and config directories...
if not exist input mkdir input
if not exist output mkdir output
if not exist config mkdir config

echo.
echo 5. Copying sample PDFs to input directory...
set pdf_count=0
for %%f in ("..\South*.pdf") do (
    if exist "%%f" (
        copy "%%f" input\
        set /a pdf_count+=1
    )
)

if %pdf_count% LSS 3 (
    echo ❌ Only %pdf_count% South of France PDFs found. Need at least 3 for testing.
    echo Please ensure South of France PDF collection is in parent directory.
    pause
    exit /b 1
)

echo ✅ Copied PDFs to input directory

echo.
echo 6. Setting up persona configuration...
if not exist "config\persona_config.json" (
    echo {> config\persona_config.json
    echo   "persona": "Travel Planner",>> config\persona_config.json
    echo   "job_to_be_done": "Plan a trip of 4 days for a group of 10 college friends.">> config\persona_config.json
    echo }>> config\persona_config.json
)

echo.
echo 7. Running Docker container...
docker run --rm -v "%cd%\input:/app/input" -v "%cd%\output:/app/output" -v "%cd%\config:/app/config" -v "%cd%\..\models:/app/models" round1b

echo.
echo 8. Results:
if exist "output\persona_analysis.json" (
    echo ✅ Docker test successful!
    echo 📄 Results saved to output\persona_analysis.json
    echo.
    echo Contents:
    type output\persona_analysis.json
) else (
    echo ❌ Docker test failed - no output file generated
)

pause