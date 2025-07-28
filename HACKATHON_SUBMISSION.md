# 🏆 Adobe Hackathon Submission Guide

## 🐳 Python Docker Submission

### Round 1A: Document Structure Extraction

**Build Command:**
```bash
cd round1a
docker build --platform linux/amd64 -t round1a:submission .
```

**Run Command:**
```bash
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none round1a:submission
```

**Expected Behavior:**
- Processes all PDFs in `/app/input` directory
- Generates corresponding `filename.json` in `/app/output` for each `filename.pdf`
- Completes within ≤10 seconds per PDF
- No network access required
- CPU-only execution (amd64)

### Round 1B: Persona-Driven Intelligence

**Prerequisites:**
```bash
# Download models first
python download_models.py
```

**Build Command:**
```bash
cd round1b
docker build --platform linux/amd64 -t round1b:submission .
```

**Run Command:**
```bash
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output -v $(pwd)/../models:/app/models --network none round1b:submission
```

**Expected Behavior:**
- Processes PDFs with persona configuration from `/app/config`
- Generates analysis JSON in `/app/output`
- Completes within ≤60 seconds for 3-10 PDFs
- Uses pre-downloaded models (≤1GB)
- No network access required
- CPU-only execution (amd64)

## 🌐 Web Interface Deployment

### Vercel Deployment

**Prerequisites:**
```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login
```

**Deploy to Vercel:**
```bash
cd adobe-scan-portal
vercel --prod
```

**Environment Variables (Vercel Dashboard):**
```env
NODE_ENV=production
PYTHONPATH=/app
MODELS_PATH=/app/models
```

**Expected Result:**
- Professional web interface deployed
- Both Round 1A and 1B accessible
- Real-time processing demonstration
- Constraint validation display

## 📋 Submission Checklist

### Round 1A ✅
- [x] Dockerfile with `--platform=linux/amd64`
- [x] Processes all PDFs in `/app/input`
- [x] Outputs JSON to `/app/output`
- [x] ≤10 second processing time
- [x] ≤200MB model constraint (no models used)
- [x] CPU-only execution
- [x] No network dependencies
- [x] README.md with approach explanation

### Round 1B ✅
- [x] Dockerfile with `--platform=linux/amd64`
- [x] Processes 3-10 PDFs with persona
- [x] Outputs analysis JSON
- [x] ≤60 second processing time
- [x] ≤1GB model constraint
- [x] CPU-only execution
- [x] No network dependencies
- [x] README.md with methodology

### Web Interface ✅
- [x] Professional Next.js application
- [x] Both challenges integrated
- [x] Real-time processing
- [x] Constraint validation
- [x] Production deployment ready

## 🚀 Quick Submission Commands

### Test Docker Containers:
```bash
# Round 1A
cd round1a
docker build --platform linux/amd64 -t round1a:test .
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none round1a:test

# Round 1B (after downloading models)
cd round1b
docker build --platform linux/amd64 -t round1b:test .
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output -v $(pwd)/../models:/app/models --network none round1b:test
```

### Deploy Web Interface:
```bash
cd adobe-scan-portal
vercel --prod
```

## 📊 Submission Highlights

### Technical Excellence:
- **Full-stack solution** with professional web interface
- **Docker containerization** meeting all constraints
- **Production-ready** code with comprehensive error handling
- **Scalable architecture** supporting multiple users

### Innovation:
- **Persona-driven intelligence** beyond basic extraction
- **Semantic understanding** of document relationships
- **Real-time constraint validation** in web interface
- **Professional demonstration** platform

### Compliance:
- **All constraints met** for both rounds
- **AMD64 compatibility** explicitly specified
- **Offline processing** with no network dependencies
- **Generic implementation** without hardcoding

## 🏆 Ready for Judging!

This submission demonstrates:
- ✅ **Technical mastery** of PDF processing and AI
- ✅ **User experience** focus with professional interface
- ✅ **Production readiness** with proper deployment
- ✅ **Innovation** in document intelligence
- ✅ **Compliance** with all hackathon requirements

**The future of PDF intelligence is here!** 🚀

---

*Adobe Hackathon 2025 - "Connecting the Dots" Challenge*
*Submission ready for evaluation*