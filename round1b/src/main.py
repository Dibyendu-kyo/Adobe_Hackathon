#!/usr/bin/env python3
"""
Round 1B: Persona-Driven Document Intelligence
Analyzes multiple PDFs and extracts relevant sections based on persona and job-to-be-done.
"""

import os
import sys
import json
from datetime import datetime
from pdf_extractor import extract_document_structure
from chunking import create_semantic_chunks
from semantic_ranker import SemanticRanker


def load_persona_config():
    """Load persona and job configuration from config file."""
    config_path = "/app/config/persona_config.json"
    
    # Default configuration if file doesn't exist
    default_config = {
        "persona": "Travel Planner",
        "job_to_be_done": "Plan a trip of 4 days for a group of 10 college friends."
    }
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get("persona", default_config["persona"]), config.get("job_to_be_done", default_config["job_to_be_done"])
        except Exception as e:
            print(f"Warning: Could not load config file: {e}")
    
    return default_config["persona"], default_config["job_to_be_done"]


def main():
    """Main entry point for Round 1B persona-driven document intelligence."""
    
    # Setup directories
    input_dir = "/app/input"
    output_dir = "/app/output"
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Find PDF files in input directory
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print("Error: No PDF files found in input directory")
        sys.exit(1)
    
    if len(pdf_files) < 3:
        print("Warning: Less than 3 PDF files found. Round 1B expects 3-10 documents.")
    
    print(f"Found {len(pdf_files)} PDF files to process")
    
    # Load persona configuration
    persona, job_to_be_done = load_persona_config()
    print(f"Persona: {persona}")
    print(f"Job to be done: {job_to_be_done}")
    
    # Initialize semantic ranker
    print("Loading semantic models...")
    ranker = SemanticRanker()
    print("Models loaded successfully")
    
    # Process each PDF and collect best chunks
    best_chunks_per_pdf = []
    pdf_paths = [os.path.join(input_dir, pdf_file) for pdf_file in pdf_files]
    
    for pdf_path in pdf_paths:
        pdf_name = os.path.basename(pdf_path)
        print(f"Processing: {pdf_name}")
        
        try:
            # Extract document structure
            outline_data, doc = extract_document_structure(pdf_path)
            
            # Create semantic chunks
            outline_json = json.dumps(outline_data, indent=2)
            chunks = create_semantic_chunks(pdf_path, outline_json)
            
            # Rank chunks for this document
            ranked = ranker.rank_chunks(chunks, persona, job_to_be_done)
            
            # Take the best chunk from this document
            if ranked:
                best_chunk = ranked[0]
                best_chunk["document"] = pdf_name
                best_chunks_per_pdf.append(best_chunk)
            
            # Close document to free memory
            if doc:
                doc.close()
                
        except Exception as e:
            print(f"Error processing {pdf_name}: {str(e)}")
            continue
    
    if not best_chunks_per_pdf:
        print("Error: No chunks could be extracted from any document")
        sys.exit(1)
    
    # Sort all best chunks by score and take top 5
    top_chunks = sorted(best_chunks_per_pdf, key=lambda x: x.get("score", 0), reverse=True)[:5]
    
    # Build output structure
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
            "refined_text": chunk.get("content", "")[:1000],  # Limit to 1000 chars
            "page_number": chunk.get("page_number", 1)
        })
    
    # Create final output
    output = {
        "metadata": {
            "input_documents": pdf_files,
            "persona": persona,
            "job_to_be_done": job_to_be_done,
            "processing_timestamp": datetime.now().isoformat()
        },
        "extracted_sections": extracted_sections,
        "subsection_analysis": subsection_analysis
    }
    
    # Save output
    output_path = os.path.join(output_dir, "persona_analysis.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=4, ensure_ascii=False)
    
    print(f"✅ Persona-driven analysis completed successfully")
    print(f"📊 Processed {len(pdf_files)} documents")
    print(f"🎯 Found {len(extracted_sections)} relevant sections")
    print(f"💾 Output saved to: {output_path}")
    
    # Also print to stdout for verification
    print("\n" + "="*50)
    print("ANALYSIS RESULTS:")
    print("="*50)
    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()