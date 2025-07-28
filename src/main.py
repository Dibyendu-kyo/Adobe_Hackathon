import os
import json
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from pdf_extractor import AdvancedPDFExtractor
from chunking import create_semantic_chunks
from semantic_ranker import SemanticRanker

def process_single_pdf(pdf_path, persona, job_to_be_done, ranker):
    """Process a single PDF and return its best chunk with ultra-aggressive optimization"""
    try:
        if not os.path.exists(pdf_path):
            return None
            
        # Use the new AdvancedPDFExtractor
        extractor = AdvancedPDFExtractor()
        outline_data, doc = extractor.extract_document_structure(pdf_path)
        outline_json = json.dumps(outline_data, indent=2)
        chunks = create_semantic_chunks(pdf_path, outline_json)
        
        # Ultra-aggressive chunk limiting for speed (max 1 chunk per PDF)
        if len(chunks) > 1:
            chunks = chunks[:1]
            
        if not chunks:
            return None
            
        ranked = ranker.rank_chunks(chunks, persona, job_to_be_done)
        
        if ranked:
            best_chunk = ranked[0]
            best_chunk["document"] = pdf_path
            return best_chunk
        return None
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return None

def main():
    start_time = time.time()
    
    # Dynamic parameters - these should come from the website/API
    # For now using HR example, but these should be passed as parameters
    pdf_paths = [
        "South of France - Cities.pdf",
        "South of France - Cuisine.pdf",
        "South of France - History.pdf",
        "South of France - Restaurants and Hotels.pdf",
        "South of France - Things to Do.pdf",
        "South of France - Tips and Tricks.pdf",
        "South of France - Traditions and Culture.pdf"
    ]

    persona = "HR professional"
    job_to_be_done = "Create and manage fillable forms for onboarding and compliance."
    
    # Load models once (cached)
    ranker = SemanticRanker()

    # Process PDFs in parallel (max 8 workers for maximum speed)
    best_chunks_per_pdf = []
    
    with ThreadPoolExecutor(max_workers=8) as executor:
        # Submit all PDF processing tasks
        future_to_pdf = {
            executor.submit(process_single_pdf, pdf_path, persona, job_to_be_done, ranker): pdf_path 
            for pdf_path in pdf_paths
        }
        
        # Collect results as they complete with aggressive timeout
        for future in as_completed(future_to_pdf, timeout=25):  # 25 second timeout
            pdf_path = future_to_pdf[future]
            try:
                result = future.result(timeout=5)  # 5 second timeout per PDF
                if result and result.get('score', 0) > 0.05:  # Very low threshold for speed
                    best_chunks_per_pdf.append(result)
            except Exception as e:
                print(f"Error processing {pdf_path}: {e}")

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
            "refined_text": chunk.get("content", "")[:300],  # Even shorter for speed
            "page_number": chunk.get("page_number", 1)
        })

    processing_time = round(time.time() - start_time, 2)
    
    output = {
        "metadata": {
            "input_documents": pdf_paths,
            "persona": persona,
            "job_to_be_done": job_to_be_done,
            "processing_timestamp": datetime.now().isoformat(),
            "processing_time_seconds": processing_time,
            "documents_processed": len(best_chunks_per_pdf),
            "sections_extracted": len(extracted_sections)
        },
        "extracted_sections": extracted_sections,
        "subsection_analysis": subsection_analysis
    }

    print(json.dumps(output, indent=4, ensure_ascii=False))
    print(f"\nProcessing completed in {processing_time} seconds")

if __name__ == "__main__":
    main()
