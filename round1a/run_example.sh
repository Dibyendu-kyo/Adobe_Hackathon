#!/bin/bash

# Round 1A Example Usage Script

echo "=============================================="
echo "Round 1A: Document Structure Extraction Test"
echo "=============================================="

echo "1. Testing Python implementation..."
python test.py

echo ""
echo "2. Building Docker container..."
docker build -t round1a .

echo ""
echo "3. Creating input and output directories..."
mkdir -p input output

echo ""
echo "4. Copying sample PDF to input directory..."
if [ -f "../sample.pdf" ]; then
    cp ../sample.pdf input/
elif [ -f "../sample1.pdf" ]; then
    cp ../sample1.pdf input/
elif [ -f "../South of France - Cities.pdf" ]; then
    cp "../South of France - Cities.pdf" input/
else
    echo "❌ No sample PDF found. Please ensure sample PDFs are in parent directory."
    exit 1
fi

echo ""
echo "5. Running Docker container..."
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  round1a

echo ""
echo "6. Results:"
if [ -f "output/document_structure.json" ]; then
    echo "✅ Docker test successful!"
    echo "📄 Results saved to output/document_structure.json"
    echo ""
    echo "Contents:"
    cat output/document_structure.json
else
    echo "❌ Docker test failed - no output file generated"
fi