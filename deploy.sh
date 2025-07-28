#!/bin/bash

# Adobe Hackathon PDF Processing - Docker Deployment Script

set -e

echo "🚀 Starting Adobe PDF Processing App Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p models
mkdir -p ssl
mkdir -p logs

# Download models if they don't exist
if [ ! -d "models/all-MiniLM-L6-v2" ]; then
    print_status "Downloading AI models..."
    python download_models.py || print_warning "Model download failed, continuing anyway..."
fi

# Build and start the application
print_status "Building Docker images..."
docker-compose build --no-cache

print_status "Starting the application..."
docker-compose up -d

# Wait for the application to start
print_status "Waiting for application to start..."
sleep 30

# Check if the application is healthy
print_status "Checking application health..."
if curl -f http://localhost:3000/api/health > /dev/null 2>&1; then
    print_success "Application is running successfully!"
    print_success "🎉 Adobe PDF Processing App is now available at:"
    print_success "   📱 Frontend: http://localhost:3000"
    print_success "   🔍 Health Check: http://localhost:3000/api/health"
    echo ""
    print_status "To view logs: docker-compose logs -f"
    print_status "To stop: docker-compose down"
    print_status "To restart: docker-compose restart"
else
    print_error "Application health check failed!"
    print_status "Checking logs..."
    docker-compose logs --tail=50
    exit 1
fi

# Show running containers
print_status "Running containers:"
docker-compose ps