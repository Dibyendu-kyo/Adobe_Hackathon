FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the web interface
COPY . .

# Copy the round implementations
COPY ../round1a/src ./round1a_src
COPY ../round1b/src ./round1b_src
COPY ../models ./models

# Create necessary directories
RUN mkdir -p uploads outputs templates

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Run the application
CMD ["python", "app.py"]