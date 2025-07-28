# Multi-stage Docker build for Adobe Hackathon PDF Processing App

# Stage 1: Build Next.js frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY adobe-scan-portal/package*.json ./
RUN npm ci --only=production
COPY adobe-scan-portal/ ./
RUN npm run build

# Stage 2: Prepare Python backend
FROM python:3.9-slim AS backend-builder
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python source code
COPY round1a/ ./round1a/
COPY round1b/ ./round1b/
COPY adobe-scan-portal/scripts/ ./scripts/

# Download models if not present
COPY download_models.py ./
RUN python download_models.py || echo "Models download failed, continuing..."

# Stage 3: Final production image
FROM python:3.9-slim AS production

# Install Node.js in the Python image
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Python dependencies and code from backend builder
COPY --from=backend-builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=backend-builder /app ./

# Copy Next.js build from frontend builder
COPY --from=frontend-builder /app/frontend/.next ./adobe-scan-portal/.next
COPY --from=frontend-builder /app/frontend/public ./adobe-scan-portal/public
COPY --from=frontend-builder /app/frontend/package*.json ./adobe-scan-portal/
COPY --from=frontend-builder /app/frontend/next.config.mjs ./adobe-scan-portal/
COPY --from=frontend-builder /app/frontend/tailwind.config.ts ./adobe-scan-portal/
COPY --from=frontend-builder /app/frontend/postcss.config.mjs ./adobe-scan-portal/
COPY --from=frontend-builder /app/frontend/components.json ./adobe-scan-portal/
COPY --from=frontend-builder /app/frontend/tsconfig.json ./adobe-scan-portal/

# Install Node.js production dependencies
WORKDIR /app/adobe-scan-portal
RUN npm ci --only=production

# Create necessary directories
RUN mkdir -p /tmp/uploads

# Set environment variables
ENV NODE_ENV=production
ENV PYTHONPATH=/app
ENV MODELS_PATH=/app/models

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:3000/api/health || exit 1

# Start the application
CMD ["npm", "start"]