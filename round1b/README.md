# Round 1B: Persona-Driven Document Intelligence

This round builds on the first by requiring a system that acts as an intelligent document analyst. The goal is to extract and prioritize the most relevant sections from a collection of documents based on a specific user's role and task.

## What You Need to Build

A system that processes:
- **Document Collection**: 3-10 related PDFs from any domain
- **Persona Definition**: A description of the user's role and expertise
- **Job-to-be-Done**: The specific task the user needs to accomplish

## Required Output

A JSON file containing:
- Metadata (input documents, persona, job, timestamp)
- List of "Extracted Sections" with document name, page number, section title, and importance rank
- "Sub-section Analysis" with refined text from extracted sections

## Constraints

- **Processing Time**: 60 seconds or less for 3-5 documents
- **Model Size**: If a model is used, its size must be 1GB or less
- **Network**: No internet access allowed during execution
- **Runtime Environment**: CPU only

## Usage

```bash
# Build the Docker container
docker build -t round1b .

# Run with PDF collection and persona config
docker run -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output -v $(pwd)/config:/app/config round1b
```

## Output Format

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
      "section_title": "Section Title",
      "importance_rank": 1,
      "page_number": 5
    }
  ],
  "subsection_analysis": [
    {
      "document": "doc1.pdf",
      "refined_text": "Refined content...",
      "page_number": 5
    }
  ]
}
```