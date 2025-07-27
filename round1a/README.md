# Round 1A: Understand Your Document

This round focuses on building a tool that can analyze a single PDF and understand its basic structure. The mission is to extract a structured outline from the document, which will serve as a foundation for later rounds.

## What You Need to Build

A solution that accepts a PDF file up to 50 pages long and extracts:
- The document's Title
- Its headings (H1, H2, H3), including the heading level and the page number where it appears
- Output as a valid JSON file

## Constraints

- **Execution Time**: 10 seconds or less for a 50-page PDF
- **Model Size**: If a model is used, its size must be 200MB or less
- **Network**: Must work offline with no internet access or network calls
- **Runtime Environment**: CPU only (amd64 architecture), 8 CPUs, 16 GB RAM
- **Container**: Must be packaged in a Docker container compatible with linux/amd64

## Usage

```bash
# Build the Docker container
docker build -t round1a .

# Run with a PDF file
docker run -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output round1a
```

## Output Format

```json
{
  "title": "Document Title",
  "outline": [
    {
      "level": "H1",
      "text": "Heading Text",
      "page": 1
    }
  ]
}
```