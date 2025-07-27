# Testing Guide for Adobe Hackathon Rounds

This guide shows you how to test both Round 1A and Round 1B implementations to verify they're working correctly.

## Quick Start

### 1. Prerequisites Check
```bash
# Run comprehensive test suite (from root directory)
python run_tests.py
```

### 2. Individual Round Testing
```bash
# Test Round 1A only (from round1a directory)
cd round1a
python test.py

# Test Round 1B only (from round1b directory, requires models)
cd round1b
python test.py
```

### 3. Validate Outputs
```bash
# Validate all generated outputs (from root directory)
python validate_outputs.py
```

## Detailed Testing Steps

### Round 1A Testing

**Prerequisites:**
- Python 3.8+
- PyMuPDF installed: `pip install PyMuPDF==1.23.14`
- At least one PDF file (sample.pdf, sample1.pdf, etc.)

**Manual Test:**
```bash
# 1. Test Python implementation
cd round1a/src
python -c "
from pdf_extractor import extract_document_structure
import json
result, doc = extract_document_structure('../../sample.pdf')
if doc: doc.close()
print(json.dumps(result, indent=2))
"

# 2. Test Docker container
cd round1a
mkdir -p input output
cp ../sample.pdf input/
docker build -t round1a .
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output round1a
cat output/document_structure.json
```

**Expected Output Format:**
```json
{
  "title": "Document Title",
  "outline": [
    {
      "level": "H1",
      "text": "Chapter 1: Introduction",
      "page": 1
    },
    {
      "level": "H2", 
      "text": "1.1 Overview",
      "page": 2
    }
  ]
}
```

**Validation Checklist:**
- ✅ Processing time ≤ 10 seconds
- ✅ Output is valid JSON
- ✅ Has "title" and "outline" keys
- ✅ Headings have level (H1/H2/H3), text, and page
- ✅ No network calls made
- ✅ Works offline

### Round 1B Testing

**Prerequisites:**
- Python 3.8+
- All dependencies: `pip install -r round1b/requirements.txt`
- Pre-downloaded models: `python download_models.py`
- 3+ PDF files (South of France collection recommended)

**Manual Test:**
```bash
# 1. Test Python implementation
python -c "
import sys
sys.path.append('round1b/src')
from semantic_ranker import SemanticRanker
ranker = SemanticRanker()
print('✅ Models loaded successfully')
"

# 2. Test full pipeline
python test_round1b.py

# 3. Test Docker container
cd round1b
mkdir -p input output config
cp ../South*.pdf input/
echo '{\"persona\": \"Travel Planner\", \"job_to_be_done\": \"Plan a trip\"}' > config/persona_config.json
docker build -t round1b .
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/../models:/app/models \
  round1b
cat output/persona_analysis.json
```

**Expected Output Format:**
```json
{
  "metadata": {
    "input_documents": ["doc1.pdf", "doc2.pdf"],
    "persona": "Travel Planner",
    "job_to_be_done": "Plan a trip",
    "processing_timestamp": "2025-01-27T..."
  },
  "extracted_sections": [
    {
      "document": "doc1.pdf",
      "section_title": "Best Restaurants",
      "importance_rank": 1,
      "page_number": 5
    }
  ],
  "subsection_analysis": [
    {
      "document": "doc1.pdf", 
      "refined_text": "Content preview...",
      "page_number": 5
    }
  ]
}
```

**Validation Checklist:**
- ✅ Processing time ≤ 60 seconds for 3-5 docs
- ✅ Model size ≤ 1GB (actual: ~184MB)
- ✅ Output is valid JSON with required structure
- ✅ Sections ranked by relevance to persona
- ✅ No network calls made
- ✅ Works offline

## Troubleshooting

### Common Issues

**Round 1A:**
- `ImportError: No module named 'fitz'` → Install PyMuPDF: `pip install PyMuPDF==1.23.14`
- Empty outline → PDF may have no clear heading structure
- Slow processing → Check PDF size (should be ≤50 pages)

**Round 1B:**
- `Models not found` → Run `python download_models.py`
- `CUDA out of memory` → Models are CPU-only, check implementation
- `ImportError: sentence_transformers` → Install dependencies: `pip install -r round1b/requirements.txt`
- Slow processing → Reduce batch sizes in semantic_ranker.py

### Performance Verification

**Round 1A Performance Test:**
```bash
python -c "
import time
from round1a.src.pdf_extractor import extract_document_structure

start = time.time()
result, doc = extract_document_structure('sample.pdf')
if doc: doc.close()
elapsed = time.time() - start

print(f'Processing time: {elapsed:.2f}s')
print(f'Constraint (≤10s): {\"✅ PASS\" if elapsed <= 10 else \"❌ FAIL\"}')
"
```

**Round 1B Performance Test:**
```bash
python -c "
import time
import sys
sys.path.append('round1b/src')
from semantic_ranker import SemanticRanker

start = time.time()
ranker = SemanticRanker()
elapsed = time.time() - start

print(f'Model loading time: {elapsed:.2f}s')
print('Note: Processing time measured during full pipeline test')
"
```

## File Locations

After running tests, check these locations for outputs:

- **Round 1A outputs:** `test_output_1a_*.json`
- **Round 1B outputs:** `test_output_1b_*.json`
- **Docker outputs:** `test_output/document_structure.json`, `test_output/persona_analysis.json`

## Success Criteria

**Round 1A Success:**
- ✅ Extracts title and headings from PDF
- ✅ Processes in ≤10 seconds
- ✅ Valid JSON output format
- ✅ Works offline, no models needed

**Round 1B Success:**
- ✅ Ranks sections by persona relevance
- ✅ Processes 3-5 docs in ≤60 seconds
- ✅ Uses models ≤1GB total size
- ✅ Valid JSON output with metadata
- ✅ Works offline with pre-downloaded models

Both implementations should now be ready for submission!