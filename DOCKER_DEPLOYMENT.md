# 🐳 Docker Deployment Guide - Adobe Hackathon PDF Processing

## 🚀 Quick Start

### Prerequisites
- Docker Desktop installed and running
- At least 4GB RAM available
- 10GB free disk space (for models and images)

### One-Click Deployment

**Windows:**
```cmd
deploy.bat
```

**Linux/Mac:**
```bash
chmod +x deploy.sh
./deploy.sh
```

## 📋 Manual Deployment Steps

### 1. Build the Docker Image
```bash
docker-compose build
```

### 2. Start the Application
```bash
docker-compose up -d
```

### 3. Check Status
```bash
# View logs
docker-compose logs -f

# Check health
curl http://localhost:3000/api/health

# View running containers
docker-compose ps
```

## 🌐 Access Points

- **Main Application**: http://localhost:3000
- **Health Check**: http://localhost:3000/api/health
- **Round 1A API**: http://localhost:3000/api/round1a
- **Round 1B API**: http://localhost:3000/api/round1b

## 🔧 Configuration

### Environment Variables
Edit `.env.production` to customize:

```env
NODE_ENV=production
PYTHONPATH=/app
MODELS_PATH=/app/models
MAX_FILES_ROUND1B=15
ROUND1A_TIMEOUT=10000
ROUND1B_TIMEOUT=120000
```

### Volume Mounts
- `./models:/app/models` - AI models persistence
- `/tmp/adobe-uploads:/tmp/uploads` - Temporary file storage

## 📊 Monitoring

### Health Check Endpoint
```bash
curl http://localhost:3000/api/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-27T...",
  "services": {
    "frontend": "running",
    "round1a": "available",
    "round1b": "available",
    "models": "loaded"
  },
  "version": "1.0.0"
}
```

### Container Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f adobe-pdf-app

# Last 100 lines
docker-compose logs --tail=100
```

## 🔄 Management Commands

### Start/Stop
```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart

# Rebuild and restart
docker-compose up -d --build
```

### Scaling (if needed)
```bash
# Scale to multiple instances
docker-compose up -d --scale adobe-pdf-app=3
```

## 🐛 Troubleshooting

### Common Issues

**1. Port 3000 already in use:**
```bash
# Check what's using the port
netstat -tulpn | grep :3000

# Kill the process or change port in docker-compose.yml
```

**2. Models not downloading:**
```bash
# Download manually
python download_models.py

# Or mount existing models
# Edit docker-compose.yml volumes section
```

**3. Out of memory:**
```bash
# Increase Docker memory limit in Docker Desktop settings
# Minimum 4GB recommended
```

**4. Python script errors:**
```bash
# Check Python dependencies
docker-compose exec adobe-pdf-app pip list

# Check Python path
docker-compose exec adobe-pdf-app python -c "import sys; print(sys.path)"
```

### Debug Mode
```bash
# Run with debug output
docker-compose up --build

# Access container shell
docker-compose exec adobe-pdf-app bash

# Check file structure
docker-compose exec adobe-pdf-app ls -la /app
```

## 🏭 Production Deployment

### With Nginx (Recommended)
```bash
# Start with nginx proxy
docker-compose --profile production up -d
```

### SSL Configuration
1. Place SSL certificates in `./ssl/` directory
2. Update `nginx.conf` with SSL configuration
3. Restart nginx service

### Environment-Specific Configs
```bash
# Development
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

## 📈 Performance Optimization

### Resource Limits
Edit `docker-compose.yml`:
```yaml
services:
  adobe-pdf-app:
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
        reservations:
          memory: 2G
          cpus: '1.0'
```

### Caching
- Models are cached in `./models` volume
- Next.js build cache is preserved
- Nginx caches static assets

## 🔒 Security

### Production Security Checklist
- [ ] Change default ports
- [ ] Enable SSL/TLS
- [ ] Set up firewall rules
- [ ] Configure rate limiting
- [ ] Enable container security scanning
- [ ] Set up log monitoring
- [ ] Configure backup strategy

### Network Security
```bash
# Create custom network
docker network create adobe-network

# Update docker-compose.yml to use custom network
```

## 📦 Backup & Recovery

### Backup Models
```bash
# Backup models directory
tar -czf models-backup.tar.gz models/
```

### Container Backup
```bash
# Export container
docker export adobe-pdf-app > adobe-app-backup.tar

# Import container
docker import adobe-app-backup.tar adobe-pdf-app:backup
```

## 🎯 Testing Deployment

### Automated Tests
```bash
# Test Round 1A
curl -X POST -F "file=@sample.pdf" http://localhost:3000/api/round1a

# Test Round 1B
curl -X POST \
  -F "files=@sample1.pdf" \
  -F "files=@sample2.pdf" \
  -F "files=@sample3.pdf" \
  -F "persona=Travel Planner" \
  -F "jobToBeDone=Plan a trip" \
  http://localhost:3000/api/round1b
```

### Load Testing
```bash
# Install Apache Bench
apt-get install apache2-utils

# Test with 100 requests, 10 concurrent
ab -n 100 -c 10 http://localhost:3000/
```

## 📞 Support

If you encounter issues:
1. Check the logs: `docker-compose logs -f`
2. Verify health endpoint: `curl http://localhost:3000/api/health`
3. Check Docker resources: `docker system df`
4. Restart services: `docker-compose restart`

## 🎉 Success!

Your Adobe Hackathon PDF Processing application is now running in Docker! 

- **Frontend**: Professional Next.js interface
- **Backend**: Python processing with AI models
- **Infrastructure**: Containerized, scalable, production-ready

Ready for hackathon demonstration! 🏆