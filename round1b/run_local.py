#!/usr/bin/env python3
"""
Local runner for Round 1B - Persona-Driven Document Intelligence
Run this from the round1b directory to test with local PDFs
"""

import os
import sys
import json
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Check if models exist
parent_dir = os.path.dirname(os.path.dirname(__file__))
models_dir = os.path.join(parent_dir, 'models')

if not os.path.exists(os.path.join(models_dir, 'all-MiniLM-L6-v2')):
    print("❌ Models not found. Please run 'python download_models.py' from the root directory first")
    sys.exit(1)

# Import Round 1B modules
try:
    from pdf_extractor import extract_document_structure
    from chunking import create_semantic_chunks
    from semantic_ranker import SemanticRanker
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def main():
    """Run Round 1B locally with PDFs from parent directory."""
    
    print("="*60)
    print("ROUND 1B: Persona-Driven Document Intelligence (Local)")
    print("="*60)
    
    # Find South of France PDFs in parent directory
    south_france_files = [
        "South of France - Cities.pdf",
        "South of France - Cuisine.pdf", 
        "South of France - History.pdf",
        "South of France - Restaurants and Hotels.pdf",
        "South of France - Things to Do.pdf",
        "South of France - Tips and Tricks.pdf",
        "South of France - Traditions and Culture.pdf"
    ]
    
    available_pdfs = []
    for pdf_file in south_france_files:
        pdf_path = os.path.join(parent_dir, pdf_file)
        if os.path.exists(pdf_path):
            available_pdfs.append(pdf_path)
    
    if len(available_pdfs) < 3:
        print(f"⚠️  Only {len(available_pdfs)} South of France PDFs found. Need at least 3.")
        print("Available:", [os.path.basename(p) for p in available_pdfs])
        return
    
    print(f"📚 Found {len(available_pdfs)} PDFs to process")
    
    # Persona selection
    personas = [
        {
            "name": "Travel Planner",
            "persona": "Travel Planner",
            "job_to_be_done": "Plan a 4-day trip for a group of 10 college friends"
        },
        {
            "name": "Food Critic",
            "persona": "Food Critic", 
            "job_to_be_done": "Write a comprehensive restaurant review guide"
        },
        {
            "name": "History Teacher",
            "persona": "History Teacher",
            "job_to_be_done": "Prepare educational content about French culture and history"
        }
    ]
    
    print("\nAvailable personas:")
    for i, persona in enumerate(personas, 1):
        print(f"  {i}. {persona['name']} - {persona['job_to_be_done']}")
    
    try:
        choice = input(f"\nSelect persona (1-{len(personas)}) or press Enter for Travel Planner: ").strip()
        if not choice:
            choice = "1"
        
        persona_index = int(choice) - 1
        if persona_index < 0 or persona_index >= len(personas):
            print("Invalid choice, using Travel Planner")
            persona_index = 0
            
    except ValueError:
        print("Invalid input, using Travel Planner")
        persona_index = 0
    
    selected_persona = personas[persona_index]
    
    print(f"\n🎭 Selected Persona: {selected_persona['persona']}")
    print(f"🎯 Job: {selected_persona['job_to_be_done']}")
    print("-" * 50)
    
    try:
        # Initialize semantic ranker
        print("🔄 Loading models...")
        ranker = SemanticRanker(model_dir=models_dir)
        
        # Process each PDF and collect chunks
        all_chunks = []
        
        for pdf_path in available_pdfs:
            pdf_name = os.path.basename(pdf_path)
            print(f"📄 Processing: {pdf_name}")
            
            # Extract structure
            outline_data, doc = extract_document_structure(pdf_path)
            
            # Create chunks
            outline_json = json.dumps(outline_data, indent=2)
            chunks = create_semantic_chunks(pdf_path, outline_json)
            
            # Rank chunks for this document
            ranked = ranker.rank_chunks(chunks, selected_persona['persona'], selected_persona['job_to_be_done'])
            
            # Take best chunk from this document
            if ranked:
                best_chunk = ranked[0]
                best_chunk["document"] = pdf_name
                all_chunks.append(best_chunk)
            
            # Close document
            if doc:
                doc.close()
        
        # Sort all chunks by score and take top 5
        top_chunks = sorted(all_chunks, key=lambda x: x.get("score", 0), reverse=True)[:5]
        
        # Build output
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
                "input_documents": [os.path.basename(p) for p in available_pdfs],
                "persona": selected_persona["persona"],
                "job_to_be_done": selected_persona["job_to_be_done"],
                "processing_timestamp": datetime.now().isoformat()
            },
            "extracted_sections": extracted_sections,
            "subsection_analysis": subsection_analysis
        }
        
        # Display results
        print(f"\n✅ Processing completed successfully!")
        print(f"📊 Extracted sections: {len(extracted_sections)}")
        print(f"📝 Subsection analysis: {len(subsection_analysis)}")
        
        print(f"\n🏆 Top relevant sections for {selected_persona['persona']}:")
        for section in extracted_sections:
            print(f"  {section['importance_rank']}. {section['section_title']}")
            print(f"     📄 {section['document']} (Page {section['page_number']})")
        
        # Save output
        persona_name = selected_persona['name'].replace(' ', '_').lower()
        output_file = f"output_{persona_name}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Output saved to: {output_file}")
        
        # Show sample of JSON output
        print(f"\n📄 JSON Output (first 50 lines):")
        print("=" * 50)
        json_str = json.dumps(result, indent=2, ensure_ascii=False)
        lines = json_str.split('\n')
        for line in lines[:50]:
            print(line)
        if len(lines) > 50:
            print("... (truncated)")
        
    except Exception as e:
        print(f"❌ Error during processing: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()