#!/bin/bash

echo "========================================"
echo "Adobe Hackathon Web Interface Launcher"
echo "========================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

echo ""
echo "Starting web interface..."
python3 run_web.py