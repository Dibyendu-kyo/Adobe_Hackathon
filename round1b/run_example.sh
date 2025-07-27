#!/bin/bash

# Round 1B Example Usage Script

echo "=================================================="
echo "Round 1B: Persona-Driven Document Intelligence Test"
echo "=================================================="

echo "1. Checking prerequisites..."
if [ ! -d "../models/all-MiniLM-L6-v2" ]; then
    echo "❌ Models not found. Please run 'python download_models.py' from root directory first."
    exit 1
fi

echo "2. Testing Python implementation..."
python test.py

echo ""
echo "3. Building Docker container..."
docker build -t round1b .

echo ""
echo "4. Creating input, output, and config directories..."
mkdir -p input output config

echo ""
echo "5. Copying sample PDFs to input directory..."
pdf_count=0
for pdf in ../South*.pdf; do
    if [ -f "$pdf" ]; then
        cp "$pdf" input/
        pdf_count=$((pdf_count + 1))
    fi
done

if [ $pdf_count -lt 3 ]; then
    echo "❌ Only $pdf_count South of France PDFs found. Need at least 3 for testing."
    echo "Please ensure South of France PDF collection is in parent directory."
    exit 1
fi

echo "✅ Copied $pdf_count PDFs to input directory"

echo ""
echo "6. Setting up persona configuration..."
if [ ! -f "config/persona_config.json" ]; then
    echo '{
  "persona": "Travel Planner",
  "job_to_be_done": "Plan a trip of 4 days for a group of 10 college friends."
}' > config/persona_config.json
fi

echo ""
echo "7. Running Docker container..."
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/../models:/app/models \
  round1b

echo ""
echo "8. Results:"
if [ -f "output/persona_analysis.json" ]; then
    echo "✅ Docker test successful!"
    echo "📄 Results saved to output/persona_analysis.json"
    echo ""
    echo "Contents:"
    cat output/persona_analysis.json
else
    echo "❌ Docker test failed - no output file generated"
fi