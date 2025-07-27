# Adobe Hackathon Web Interface

A web-based interface for both Round 1A (Document Structure Extraction) and Round 1B (Persona-Driven Document Intelligence) of the Adobe India Hackathon.

## Features

### Round 1A: Document Structure Extraction
- **Single PDF Upload**: Drag & drop or click to upload
- **Real-time Processing**: Extract title and headings in <10 seconds
- **Interactive Results**: View extracted structure with hierarchy
- **JSON Download**: Download results in required format
- **Constraint Monitoring**: Real-time validation of time and format constraints

### Round 1B: Persona-Driven Document Intelligence
- **Multiple PDF Upload**: Upload 3-10 related documents
- **Persona Configuration**: Define user role and job requirements
- **Semantic Analysis**: AI-powered relevance ranking
- **Interactive Results**: View top relevant sections
- **JSON Download**: Download analysis results

## Quick Start

### Method 1: Using the Startup Script (Recommended)
```bash
cd web_interface
python run_web.py
```

### Method 2: Manual Setup
```bash
cd web_interface

# Install dependencies
pip install -r requirements.txt

# Ensure models are downloaded (for Round 1B)
cd ..
python download_models.py
cd web_interface

# Start the web server
python app.py
```

### Method 3: Docker
```bash
cd web_interface
docker build -t adobe-hackathon-web .
docker run -p 5000:5000 adobe-hackathon-web
```

## Access the Interface

Once started, open your browser and go to:
- **Local**: http://localhost:5000
- **Network**: http://your-ip:5000

## Interface Overview

### Home Page (`/`)
- Challenge selection (Round 1A vs Round 1B)
- System status and requirements
- Usage instructions

### Round 1A Page (`/round1a`)
- PDF upload area with drag & drop
- Real-time processing status
- Results display with constraint validation
- JSON output preview and download

### Round 1B Page (`/round1b`)
- Multiple PDF upload with file management
- Persona and job configuration
- Semantic processing with progress indicator
- Ranked results display and download

## API Endpoints

### Round 1A Processing
```
POST /api/round1a/process
Content-Type: multipart/form-data

Parameters:
- pdf_file: PDF file to process

Response:
{
  "success": true,
  "processing_time": 2.34,
  "title": "Document Title",
  "headings_count": 15,
  "result": { ... },
  "output_file": "round1a_output_20250127_123456.json",
  "constraints_met": {
    "time_limit": true,
    "format_valid": true
  }
}
```

### Round 1B Processing
```
POST /api/round1b/process
Content-Type: multipart/form-data

Parameters:
- pdf_files: Array of PDF files (3-10 files)
- persona: User persona description
- job_to_be_done: Task description

Response:
{
  "success": true,
  "processing_time": 45.67,
  "documents_processed": 5,
  "extracted_sections": 5,
  "result": { ... },
  "output_file": "round1b_output_20250127_123456.json",
  "constraints_met": {
    "time_limit": true,
    "format_valid": true
  }
}
```

### File Download
```
GET /api/download/<filename>
```

### System Status
```
GET /api/status

Response:
{
  "round1a_available": true,
  "round1b_available": true,
  "models_loaded": true,
  "upload_limit_mb": 50
}
```

## Configuration

### File Upload Limits
- **Maximum file size**: 50MB per file
- **Round 1A**: Single PDF file
- **Round 1B**: 3-10 PDF files

### Processing Constraints
- **Round 1A**: ≤10 seconds processing time
- **Round 1B**: ≤60 seconds processing time
- **Models**: Automatically loaded from `../models/` directory

### Directory Structure
```
web_interface/
├── app.py                 # Main Flask application
├── run_web.py            # Startup script
├── requirements.txt      # Python dependencies
├── Dockerfile           # Docker configuration
├── templates/           # HTML templates
│   ├── base.html        # Base template
│   ├── index.html       # Home page
│   ├── round1a.html     # Round 1A interface
│   └── round1b.html     # Round 1B interface
├── uploads/             # Temporary file uploads
└── outputs/             # Generated output files
```

## Dependencies

### Python Packages
- **Flask**: Web framework
- **PyMuPDF**: PDF processing
- **sentence-transformers**: Semantic models (Round 1B)
- **torch**: ML framework (Round 1B)
- **transformers**: NLP models (Round 1B)

### Frontend
- **Bootstrap 5**: UI framework
- **Font Awesome**: Icons
- **Vanilla JavaScript**: Interactive functionality

## Features

### User Experience
- **Responsive Design**: Works on desktop and mobile
- **Drag & Drop**: Intuitive file upload
- **Real-time Feedback**: Processing status and progress
- **Error Handling**: Clear error messages and recovery
- **Download Management**: Easy access to results

### Technical Features
- **Generic Implementation**: No hardcoded values
- **Constraint Validation**: Real-time compliance checking
- **Memory Management**: Automatic cleanup of temporary files
- **Security**: File type validation and secure uploads
- **Performance**: Optimized for fast processing

## Troubleshooting

### Round 1B Not Available
```bash
# Download required models
cd ..
python download_models.py
cd web_interface
python run_web.py
```

### Port Already in Use
```bash
# Change port in app.py or use environment variable
export FLASK_PORT=8000
python app.py
```

### File Upload Issues
- Check file size (≤50MB)
- Ensure PDF format
- Verify sufficient disk space

### Processing Errors
- Check console logs for detailed error messages
- Ensure all dependencies are installed
- Verify model files are present (Round 1B)

## Development

### Adding New Features
1. Update `app.py` for new API endpoints
2. Modify templates for UI changes
3. Update requirements.txt for new dependencies

### Testing
```bash
# Test Round 1A
curl -X POST -F "pdf_file=@sample.pdf" http://localhost:5000/api/round1a/process

# Test Round 1B
curl -X POST \
  -F "pdf_files=@doc1.pdf" \
  -F "pdf_files=@doc2.pdf" \
  -F "pdf_files=@doc3.pdf" \
  -F "persona=Travel Planner" \
  -F "job_to_be_done=Plan a trip" \
  http://localhost:5000/api/round1b/process
```

## Production Deployment

### Using Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Docker
```bash
docker build -t adobe-hackathon-web .
docker run -d -p 5000:5000 --name hackathon-web adobe-hackathon-web
```

### Environment Variables
- `FLASK_ENV`: Set to `production` for production deployment
- `FLASK_PORT`: Custom port (default: 5000)
- `MAX_CONTENT_LENGTH`: Upload size limit (default: 50MB)

## License

This web interface is part of the Adobe India Hackathon submission and follows the same licensing terms as the main project.