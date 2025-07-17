import sys
sys.path.append('src')
from pdf_extractor import extract_pdf_outline
from chunking import create_semantic_chunks
from semantic_ranker import SemanticRanker

# Extract and process
outline_json = extract_pdf_outline('sample.pdf')
chunks = create_semantic_chunks('sample.pdf', outline_json)

# Test with relevant query for your CS resume
ranker = SemanticRanker()
persona = "I am a hiring manager for a software engineering position"
job_to_be_done = "Find relevant technical skills, projects, and programming experience"
ranked = ranker.rank_chunks(chunks, persona, job_to_be_done)

print("Top ranked chunks for software engineering role:")
for i, chunk in enumerate(ranked[:3], 1):
    print(f"\n#{i}:")
    print(f"Section: {chunk['section_title']}")
    print(f"Score: {chunk['score']:.4f}")
    print(f"Content preview: {chunk['content'][:300]}...")