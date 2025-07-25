import os
import json
from datetime import datetime
from pdf_extractor import extract_document_structure
from chunking import create_semantic_chunks
from semantic_ranker import SemanticRanker


def main():
    pdf_paths = [
        "South of France - Cities.pdf",
        "South of France - Cuisine.pdf",
        "South of France - History.pdf",
        "South of France - Restaurants and Hotels.pdf",
        "South of France - Things to Do.pdf",
        "South of France - Tips and Tricks.pdf",
        "South of France - Traditions and Culture.pdf"
    ]

    persona = "Travel Planner"
    job_to_be_done = "Plan a trip of 4 days for a group of 10 college friends."
    ranker = SemanticRanker()

    # For each PDF, get the best chunk (highest score)
    best_chunks_per_pdf = []

    for pdf_path in pdf_paths:
        if not os.path.exists(pdf_path):
            print(f"File not found: {pdf_path}")
            continue
        outline_data, doc = extract_document_structure(pdf_path)
        outline_json = json.dumps(outline_data, indent=2)
        chunks = create_semantic_chunks(pdf_path, outline_json)
        ranked = ranker.rank_chunks(chunks, persona, job_to_be_done)
        if ranked:
            best_chunk = ranked[0]
            best_chunk["document"] = pdf_path
            best_chunks_per_pdf.append(best_chunk)

    # Sort the best chunks from each PDF by score, take top 5
    top_chunks = sorted(best_chunks_per_pdf, key=lambda x: x.get("score", 0), reverse=True)[:5]

    extracted_sections = []
    subsection_analysis = []

    for idx, chunk in enumerate(top_chunks, 1):
        extracted_sections.append({
            "document": chunk["document"],
            "section_title": chunk.get("section_title", ""),
            "importance_rank": idx,
            "page_number": chunk.get("page_number", 1)
        })
        subsection_analysis.append({
            "document": chunk["document"],
            "refined_text": chunk.get("content", "")[:1000],
            "page_number": chunk.get("page_number", 1)
        })

    output = {
        "metadata": {
            "input_documents": pdf_paths,
            "persona": persona,
            "job_to_be_done": job_to_be_done,
            "processing_timestamp": datetime.now().isoformat()
        },
        "extracted_sections": extracted_sections,
        "subsection_analysis": subsection_analysis
    }

    print(json.dumps(output, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    main()
