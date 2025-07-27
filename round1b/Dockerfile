FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Copy pre-downloaded models (these should be mounted or copied)
# The models directory should be mounted at runtime: -v $(pwd)/models:/app/models

# Create input, output, and config directories
RUN mkdir -p /app/input /app/output /app/config

# Set the entry point
CMD ["python", "src/main.py"]