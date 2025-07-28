# Multi-stage build for universal deployment
FROM python:3.11-slim as python-base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Set working directory
WORKDIR /app

# Copy Python requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python source code
COPY round1a/ ./round1a/
COPY round1b/ ./round1b/
COPY download_models.py .

# Download AI models
RUN python download_models.py

# Copy Next.js application
COPY adobe-scan-portal/ ./adobe-scan-portal/

# Install Node.js dependencies and build
WORKDIR /app/adobe-scan-portal
RUN npm install
RUN npm run build

# Production stage
FROM python:3.11-slim as production

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Set working directory
WORKDIR /app

# Copy Python dependencies
COPY --from=python-base /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=python-base /usr/local/bin /usr/local/bin

# Copy application files
COPY --from=python-base /app/round1a ./round1a
COPY --from=python-base /app/round1b ./round1b
COPY --from=python-base /app/models ./models
COPY --from=python-base /app/adobe-scan-portal ./adobe-scan-portal

# Set environment variables
ENV NODE_ENV=production
ENV PYTHONPATH=/app
ENV MODELS_PATH=/app/models
ENV PORT=3000

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/api/health || exit 1

# Start the application
WORKDIR /app/adobe-scan-portal
CMD ["npm", "start", "--", "--hostname", "0.0.0.0", "--port", "3000"]