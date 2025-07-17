from pdf_extractor import (
    extract_document_structure
)
from chunking import create_semantic_chunks
from semantic_ranker import SemanticRanker

import json

def main():
    pdf_path = "sample.pdf"  # replace with your file

    # Step 1: Extract outline as JSON
    outline_data, doc = extract_document_structure(pdf_path)
    outline_json = json.dumps(outline_data, indent=2)
    print("Outline JSON:")
    print(outline_json)

    # Step 2: Segment into chunks
    chunks = create_semantic_chunks(pdf_path, outline_json)
    print(f"Extracted {len(chunks)} chunks.")

    # Step 3: Run semantic ranker
    ranker = SemanticRanker()
    persona = "I am a legal researcher"
    job_to_be_done = "Summarize important sections relevant to contract law"
    ranked = ranker.rank_chunks(chunks, persona, job_to_be_done)

    # Show top 3
    print("\nTop ranked chunks:")
    for i, chunk in enumerate(ranked[:3], 1):
        print(f"\n#{i}:")
        print(f"Section: {chunk['section_title']}")
        print(f"Score: {chunk['score']:.4f}")
        print(f"Text: {chunk['content'][:200]}...")

if __name__ == "__main__":
    main()
