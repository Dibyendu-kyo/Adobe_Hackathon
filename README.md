# Adobe Hackathon 2025 - Connecting the Dots Challenge

## 🎯 Project Overview

This project implements both **Round 1A** (Document Structure Extraction) and **Round 1B** (Persona-Driven Document Intelligence) challenges for the Adobe Hackathon 2025, along with a professional web interface for demonstration.

## 🏗️ Project Structure

```
Adobe_Hackathon/
├── round1a/                    # Round 1A: Document Structure Extraction
│   ├── src/                    # Core extraction logic
│   ├── input/                  # Input PDFs directory
│   ├── output/                 # Output JSON directory
│   ├── Dockerfile              # Docker container for Round 1A
│   ├── requirements.txt        # Python dependencies
│   ├── run_local.py           # Local execution script
│   └── README.md              # Round 1A documentation
├── round1b/                    # Round 1B: Persona-Driven Intelligence
│   ├── src/                    # Core intelligence logic
│   ├── config/                 # Configuration files
│   ├── Dockerfile              # Docker container for Round 1B
│   ├── requirements.txt        # Python dependencies
│   ├── run_local.py           # Local execution script
│   └── README.md              # Round 1B documentation
├── adobe-scan-portal/          # Professional Web Interface
│   ├── app/                    # Next.js application
│   ├── components/             # React components
│   ├── scripts/                # Python processing scripts
│   ├── package.json            # Node.js dependencies
│   └── README.md              # Web interface documentation
├── models/                     # AI models directory
├── Dockerfile                  # Main Docker container
├── docker-compose.yml          # Container orchestration
├── deploy.bat                  # Windows deployment script
├── deploy.sh                   # Linux/Mac deployment script
├── download_models.py          # Model download utility
├── requirements.txt            # Root Python dependencies
├── sample.pdf                  # Sample input PDF
├── sample1.pdf                 # Additional sample PDF
└── README.md                   # This file
```

## 🚀 Quick Start

### Option 1: Docker Deployment (Recommended)

**Windows:**
```cmd
deploy.bat
```

**Linux/Mac:**
```bash
chmod +x deploy.sh
./deploy.sh
```

**Manual Docker:**
```bash
docker-compose up -d
```

### Option 2: Individual Round Testing

**Round 1A:**
```bash
cd round1a
python run_local.py
```

**Round 1B:**
```bash
cd round1b
python run_local.py
```

## 🌐 Web Interface

After deployment, access the professional web interface at:
- **Main Application**: http://localhost:3000
- **Health Check**: http://localhost:3000/api/health

### Features:
- ✅ **Round 1A**: Single PDF structure extraction
- ✅ **Round 1B**: Multi-PDF persona-driven analysis (3-15 PDFs)
- ✅ **Professional UI**: Modern, responsive design
- ✅ **Real-time Processing**: Live feedback and results
- ✅ **File Management**: Drag & drop, individual removal
- ✅ **Constraint Validation**: Real-time compliance checking

## 📋 Challenge Requirements

### Round 1A: Document Structure Extraction
- **Input**: Single PDF (up to 50 pages)
- **Output**: JSON with title and headings (H1, H2, H3)
- **Constraints**: ≤10s processing, ≤200MB models, CPU only
- **Format**: Hierarchical structure with page numbers

### Round 1B: Persona-Driven Intelligence
- **Input**: 3-15 related PDFs + persona + job description
- **Output**: JSON with ranked relevant sections
- **Constraints**: ≤60s processing, ≤1GB models, CPU only
- **Format**: Metadata + extracted sections + subsection analysis

## 🔧 Technical Stack

### Backend:
- **Python 3.9+**: Core processing logic
- **PyMuPDF**: PDF text extraction
- **Sentence Transformers**: Semantic analysis
- **Scikit-learn**: Machine learning utilities
- **TensorFlow**: AI model support

### Frontend:
- **Next.js 15**: React framework
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Modern styling
- **Framer Motion**: Smooth animations
- **Radix UI**: Accessible components

### Infrastructure:
- **Docker**: Containerization
- **Docker Compose**: Multi-service orchestration
- **Nginx**: Reverse proxy (production)
- **Health Checks**: Service monitoring

## � Key Features

### Round 1A Capabilities:
- **Generic PDF Processing**: Works with any PDF format
- **Intelligent Heading Detection**: Beyond font-size analysis
- **Hierarchical Structure**: Proper H1/H2/H3 classification
- **Fast Processing**: Sub-10 second extraction
- **Multilingual Support**: Handles various languages

### Round 1B Capabilities:
- **Semantic Understanding**: AI-powered content analysis
- **Persona Matching**: Context-aware section ranking
- **Multi-document Analysis**: Processes 3-15 PDFs simultaneously
- **Intelligent Filtering**: Removes irrelevant content
- **Detailed Insights**: Granular subsection analysis

### Web Interface Features:
- **Dual Challenge Support**: Both Round 1A and 1B
- **Professional Design**: Clean, modern interface
- **Real-time Feedback**: Live processing indicators
- **File Management**: Intuitive upload and organization
- **Results Visualization**: Clear, structured output display
- **Responsive Design**: Works on all devices

## 📊 Performance Metrics

### Round 1A:
- **Processing Time**: ~2-5 seconds for typical PDFs
- **Memory Usage**: <500MB peak
- **Accuracy**: High precision heading detection
- **Model Size**: <200MB (constraint compliant)

### Round 1B:
- **Processing Time**: ~30-60 seconds for 5-10 PDFs
- **Memory Usage**: <2GB peak
- **Model Size**: ~800MB (constraint compliant)
- **Relevance**: High-quality persona-driven results

## 🔒 Security & Compliance

- **Offline Processing**: No internet dependencies
- **Data Privacy**: All processing happens locally
- **Container Security**: Isolated execution environment
- **Input Validation**: Comprehensive file and parameter checking
- **Resource Limits**: Proper memory and CPU constraints

## 🏆 Hackathon Compliance

### ✅ All Requirements Met:
- **Docker Compatibility**: AMD64 architecture support
- **Constraint Compliance**: Time, memory, and model size limits
- **Offline Operation**: No network dependencies
- **Generic Implementation**: No hardcoded logic
- **Professional Presentation**: Production-ready interface

### 📈 Scoring Optimization:
- **High Accuracy**: Optimized heading detection algorithms
- **Performance**: Fast processing within constraints
- **User Experience**: Professional, intuitive interface
- **Code Quality**: Clean, maintainable, documented code

## 🛠️ Development

### Prerequisites:
- Docker Desktop
- Python 3.9+
- Node.js 18+
- 8GB+ RAM
- 10GB+ disk space

### Local Development:
```bash
# Install Python dependencies
pip install -r requirements.txt

# Download AI models
python download_models.py

# Install Node.js dependencies
cd adobe-scan-portal
npm install

# Start development server
npm run dev
```

## 📞 Support

For issues or questions:
1. Check the logs: `docker-compose logs -f`
2. Verify health: `curl http://localhost:3000/api/health`
3. Review individual round READMEs
4. Check Docker resources: `docker system df`

## 🎉 Ready for Hackathon!

This project demonstrates:
- ✅ **Technical Excellence**: Robust, scalable implementation
- ✅ **User Experience**: Professional, intuitive interface
- ✅ **Innovation**: Advanced AI-powered document intelligence
- ✅ **Compliance**: All hackathon requirements met
- ✅ **Production Ready**: Containerized, deployable solution

**The future of PDF intelligence starts here!** 🚀 
live link https://adobe-hackathon.vercel.app/
