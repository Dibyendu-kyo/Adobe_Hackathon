# Dynamic Persona Testing Framework

A flexible, configurable system for testing PDF semantic ranking with different personas - **no hardcoding required!**

## Features

✅ **Configuration-driven**: Define personas in JSON, not code  
✅ **Command-line interface**: Run custom scenarios on-demand  
✅ **Extensible**: Add new personas without touching code  
✅ **Flexible output**: Configurable scoring, preview length, filtering  
✅ **Works everywhere**: Any PDF, any persona, any job-to-be-done  

## Quick Start

### 1. Run All Configured Scenarios
```bash
python test_personas.py sample.pdf
```

### 2. Test Custom Persona
```bash
python test_personas.py sample.pdf --persona "I am a cybersecurity expert" --job "Find security vulnerabilities and best practices"
```

### 3. Run Specific Scenario
```bash
python test_personas.py sample.pdf --scenario "Data Science"
```

### 4. Use Different PDF
```bash
python test_personas.py my_document.pdf --scenario "Academic Research"
```

## Configuration

Edit `personas_config.json` to add new scenarios:

```json
{
  "test_scenarios": [
    {
      "name": "Your Custom Scenario",
      "persona": "I am a [role] with expertise in [domain]",
      "job_to_be_done": "I need to [specific task]",
      "expected_keywords": ["keyword1", "keyword2"]
    }
  ],
  "output_settings": {
    "top_results": 3,
    "show_scores": true,
    "preview_length": 150,
    "score_threshold": -10.0
  }
}
```

## Real-World Examples

### Academic Research
```bash
python test_personas.py research_paper.pdf \
  --persona "PhD student in machine learning" \
  --job "Find methodology and experimental setup details"
```

### Business Analysis
```bash
python test_personas.py annual_report.pdf \
  --persona "Investment analyst" \
  --job "Analyze financial performance and growth strategies"
```

### Technical Documentation
```bash
python test_personas.py api_docs.pdf \
  --persona "Software developer" \
  --job "Find authentication and error handling examples"
```

## Command Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `pdf_path` | PDF file to analyze | `document.pdf` |
| `--config` | Custom config file | `--config my_config.json` |
| `--persona` | Custom persona | `--persona "I am a data scientist"` |
| `--job` | Custom job-to-be-done | `--job "Find ML model details"` |
| `--scenario` | Run specific scenario | `--scenario "Business Analysis"` |

## Output Format

```
======================================================================
SCENARIO: Data Science
PERSONA: Data Scientist specializing in NLP
JOB: Identify machine learning models, semantic embeddings, and vector search techniques
======================================================================

Top 3 most relevant sections:

#1 (Score: 2.6822)
Section: 2.2 Selecting the Ideal On-Device Embedding Model
Page: 10
Preview: The success of the semantic search architecture hinges on...

#2 (Score: 2.1582)
Section: 2.1 From Structure to Semantics: The Core Intelligence Architecture
Page: 9
Preview: The most robust, scalable, and generalizable architecture...
```

## Key Benefits

### 🎯 **Semantic Understanding**
- Higher scores = more relevant content
- Positive scores indicate strong semantic match
- Negative scores show relative ranking

### 🔧 **Fully Configurable**
- No code changes needed for new personas
- Adjustable output settings
- Extensible scenario library

### 🚀 **Production Ready**
- Works with any PDF document
- Handles diverse domains and personas
- Offline operation (no internet required)

### 📊 **Measurable Results**
- Quantified relevance scores
- Consistent ranking methodology
- Comparable across different personas

## Advanced Usage

### Adding New Scenarios Programmatically
```python
from test_personas import PersonaTester

tester = PersonaTester()
tester.add_scenario(
    name="Legal Analysis",
    persona="Corporate lawyer",
    job_to_be_done="Find contract terms and compliance requirements",
    expected_keywords=["contract", "compliance", "legal", "terms"]
)
tester.save_config()
```

### Batch Processing Multiple PDFs
```python
pdfs = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
for pdf in pdfs:
    results = tester.run_all_scenarios(pdf)
    # Process results...
```

This framework demonstrates how semantic search can provide **personalized, intelligent document analysis** without any hardcoded logic - exactly what modern AI systems need!