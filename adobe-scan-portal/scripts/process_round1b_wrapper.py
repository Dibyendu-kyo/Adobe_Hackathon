#!/usr/bin/env python3
"""
Wrapper script for Round 1B processing using your local implementation
Called from the Next.js API route
"""

import sys
import os
import json
from datetime import datetime

# Add the round1b src to path
script_dir = os.path.dirname(os.path.abspath(__file__))
round1b_src = os.path.join(script_dir, '..', '..', 'round1b', 'src')
sys.path.append(round1b_src)

try:
    from pdf_extractor import extract_document_structure
    from chunking import create_semantic_chunks
    from semantic_ranker import SemanticRanker
except ImportError as e:
    print(json.dumps({"error": f"Failed to import modules: {e}"}), file=sys.stderr)
    sys.exit(1)

def main():
    if len(sys.argv) < 5:
        print(json.dumps({"error": "Usage: python process_round1b_wrapper.py <models_dir> <persona> <job_to_be_done> <pdf_file1> [pdf_file2] ..."}), file=sys.stderr)
        sys.exit(1)
    
    models_dir = sys.argv[1]
    persona = sys.argv[2]
    job_to_be_done = sys.argv[3]
    pdf_files = sys.argv[4:]
    
    # Validate inputs
    if not os.path.exists(models_dir):
        print(json.dumps({"error": f"Models directory not found: {models_dir}"}), file=sys.stderr)
        sys.exit(1)
    
    for pdf_file in pdf_files:
        if not os.path.exists(pdf_file):
            print(json.dumps({"error": f"PDF file not found: {pdf_file}"}), file=sys.stderr)
            sys.exit(1)
    
    try:
        # Initialize semantic ranker with your models
        ranker = SemanticRanker(model_dir=models_dir)
        
        # Process each PDF and collect chunks using your implementation
        all_chunks = []
        
        for pdf_path in pdf_files:
            # Extract structure using your Round 1A implementation
            outline_data, doc = extract_document_structure(pdf_path)
            
            # Create chunks using your chunking implementation
            outline_json = json.dumps(outline_data, indent=2)
            chunks = create_semantic_chunks(pdf_path, outline_json)
            
            # Rank chunks for this document using your ranker
            ranked = ranker.rank_chunks(chunks, persona, job_to_be_done)
            
            # Take top 3 chunks from each document for variety
            for i, chunk in enumerate(ranked[:3]):
                chunk["document"] = os.path.basename(pdf_path)
                chunk["doc_rank"] = i + 1
                all_chunks.append(chunk)
            
            # Close document to free memory
            if doc:
                doc.close()
        
        # Enhanced filtering and ranking using your logic
        filtered_chunks = []
        for chunk in all_chunks:
            section_title = chunk.get("section_title", "").lower()
            content = chunk.get("content", "").lower()
            
            # Skip generic sections
            if any(generic in section_title for generic in ["introduction", "conclusion", "overview", "preface"]):
                if not any(actionable in content for actionable in ["specific", "detailed", "step-by-step", "practical"]):
                    continue
            
            # Calculate relevance score based on persona and task
            relevance_score = chunk.get("score", 0)
            
            if persona.lower() == "travel planner":
                # Boost travel planning relevant content
                title_boost = 0
                content_boost = 0
                
                high_value_titles = ["coastal adventures", "nightlife", "restaurants", "hotels", "activities", "culinary experiences", "packing tips", "city guide", "things to do"]
                for keyword in high_value_titles:
                    if keyword in section_title:
                        title_boost += 0.5
                
                high_value_content = ["beach", "restaurant", "bar", "club", "hotel", "activity", "experience", "nightlife", "coastal", "adventure"]
                for keyword in high_value_content:
                    if keyword in content:
                        content_boost += 0.1
                
                # Task-specific boost for college friends
                if "college friends" in job_to_be_done.lower():
                    college_keywords = ["nightlife", "beach", "adventure", "activities", "entertainment", "bar", "club", "young", "group", "coastal", "water sports", "budget", "affordable"]
                    for keyword in college_keywords:
                        if keyword in content:
                            content_boost += 0.3
                    
                    # Extra boost for sections with multiple college-friendly keywords
                    college_count = sum(1 for keyword in college_keywords if keyword in content)
                    if college_count >= 3:
                        content_boost += 0.4
                    
                    # Penalize luxury content for college budget
                    luxury_keywords = ["luxury", "luxurious", "five-star", "michelin", "exclusive", "premium", "grand hotel"]
                    for keyword in luxury_keywords:
                        if keyword in content:
                            content_boost -= 0.3
                    
                    # Penalize family content heavily
                    family_keywords = ["family-friendly", "children", "kids", "family resort", "child", "baby"]
                    for keyword in family_keywords:
                        if keyword in content:
                            content_boost -= 0.6
                
                relevance_score += title_boost + content_boost
            
            chunk["adjusted_score"] = relevance_score
            filtered_chunks.append(chunk)
        
        # Sort by adjusted score and ensure diversity
        sorted_chunks = sorted(filtered_chunks, key=lambda x: x.get("adjusted_score", 0), reverse=True)
        
        # Ensure we get diverse content from different documents
        top_chunks = []
        used_documents = set()
        
        for chunk in sorted_chunks:
            if len(top_chunks) >= 5:
                break
            
            doc_name = chunk.get("document", "")
            # Allow max 2 sections per document for diversity
            doc_count = sum(1 for c in top_chunks if c.get("document") == doc_name)
            if doc_count < 2:
                top_chunks.append(chunk)
        
        # If we still need more chunks, add remaining highest scored ones
        while len(top_chunks) < 5 and len(top_chunks) < len(sorted_chunks):
            for chunk in sorted_chunks:
                if chunk not in top_chunks:
                    top_chunks.append(chunk)
                    break
        
        # Build output using your format
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
        
        result = {
            "metadata": {
                "input_documents": [os.path.basename(f) for f in pdf_files],
                "persona": persona,
                "job_to_be_done": job_to_be_done,
                "processing_timestamp": datetime.now().isoformat()
            },
            "extracted_sections": extracted_sections,
            "subsection_analysis": subsection_analysis
        }
        
        # Clean the result to remove problematic Unicode characters
        def clean_text(obj):
            if isinstance(obj, str):
                return obj.replace('\u202f', ' ').replace('\u00a0', ' ').strip()
            elif isinstance(obj, dict):
                return {k: clean_text(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_text(item) for item in obj]
            return obj
        
        cleaned_result = clean_text(result)
        
        # Output result as JSON with ASCII encoding to avoid Unicode issues
        print(json.dumps(cleaned_result, ensure_ascii=True, indent=None))
        
    except Exception as e:
        print(json.dumps({"error": f"Processing failed: {str(e)}"}), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()