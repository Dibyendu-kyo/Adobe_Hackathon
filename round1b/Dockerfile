FROM --platform=linux/amd64 python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY config/ ./config/

# Copy models (should be pre-downloaded)
COPY ../models/ ./models/

# Create input and output directories
RUN mkdir -p /app/input /app/output

# Set the entry point to process PDFs with persona analysis
CMD ["python", "src/main.py"]