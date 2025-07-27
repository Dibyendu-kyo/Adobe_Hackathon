# Adobe India Hackathon - Separated Challenges

This repository contains the separated implementations for Round 1A and Round 1B of the Adobe India Hackathon.

## Project Structure

```
├── round1a/                    # Round 1A: Document Structure Extraction
│   ├── src/
│   │   ├── main.py            # Main entry point for Round 1A
│   │   └── pdf_extractor.py   # PDF structure extraction logic
│   ├── Dockerfile             # Docker container for Round 1A
│   ├── requirements.txt       # Dependencies for Round 1A
│   ├── README.md             # Round 1A documentation
│   └── run_example.sh        # Example usage script
│
├── round1b/                    # Round 1B: Persona-Driven Intelligence
│   ├── src/
│   │   ├── main.py            # Main entry point for Round 1B
│   │   ├── pdf_extractor.py   # PDF structure extraction (shared logic)
│   │   ├── chunking.py        # Semantic chunking logic
│   │   └── semantic_ranker.py # Semantic ranking with transformers
│   ├── config/
│   │   └── persona_config.json # Persona and job configuration
│   ├── Dockerfile             # Docker container for Round 1B
│   ├── requirements.txt       # Dependencies for Round 1B
│   ├── README.md             # Round 1B documentation
│   └── run_example.sh        # Example usage script
│
├── models/                     # Pre-downloaded ML models (shared)
├── *.pdf                      # Sample PDF files
└── README.md                  # This file
```

## Round 1A: Understand Your Document

**Objective**: Extract structured outline (title and headings) from a single PDF document.

**Key Features**:
- Lightweight implementation using only PyMuPDF
- Fast processing (≤10 seconds for 50-page PDF)
- Small model size (≤200MB)
- Offline operation
- CPU-only execution

**Usage**:
```bash
cd round1a
./run_example.sh
```

## Round 1B: Persona-Driven Document Intelligence

**Objective**: Analyze multiple PDFs and extract relevant sections based on user persona and job-to-be-done.

**Key Features**:
- Processes 3-10 related PDF documents
- Uses semantic similarity models for content ranking
- Persona-driven relevance scoring
- Fast processing (≤60 seconds for 3-5 documents)
- Model size ≤1GB
- Offline operation

**Usage**:
```bash
cd round1b
./run_example.sh
```

## Models

Both challenges use pre-downloaded models stored in the `models/` directory:
- `all-MiniLM-L6-v2`: Sentence embedding model for semantic similarity
- `cross-encoder-ms-marco-MiniLM-L6-v2`: Cross-encoder for re-ranking

Download models using:
```bash
python download_models.py
```

## Key Differences

| Aspect | Round 1A | Round 1B |
|--------|----------|----------|
| Input | Single PDF | 3-10 PDFs |
| Output | Document structure | Ranked relevant sections |
| Dependencies | PyMuPDF only | PyMuPDF + Transformers |
| Processing Time | ≤10 seconds | ≤60 seconds |
| Model Size | ≤200MB | ≤1GB |
| Complexity | Simple extraction | Semantic analysis |

## Docker Usage

Each round has its own Docker container:

**Round 1A**:
```bash
docker build -t round1a ./round1a
docker run -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output round1a
```

**Round 1B**:
```bash
docker build -t round1b ./round1b
docker run -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output -v $(pwd)/config:/app/config -v $(pwd)/models:/app/models round1b
```