#!/usr/bin/env python3
"""
Test script for Round 1B - Persona-Driven Document Intelligence
Run from round1b directory: python test.py
"""

import os
import sys
import json
import time
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


def test_round1b():
    """Test Round 1B implementation with sample PDFs."""
    
    print("="*60)
    print("TESTING ROUND 1B: Persona-Driven Document Intelligence")
    print("="*60)
    
    # Look for South of France PDFs in parent directory
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    
    test_pdfs = []
    south_france_files = [
        "South of France - Cities.pdf",
        "South of France - Cuisine.pdf", 
        "South of France - History.pdf",
        "South of France - Restaurants and Hotels.pdf",
        "South of France - Things to Do.pdf",
        "South of France - Tips and Tricks.pdf",
        "South of France - Traditions and Culture.pdf"
    ]
    
    for pdf_file in south_france_files:
        pdf_path = os.path.join(parent_dir, pdf_file)
        if os.path.exists(pdf_path):
            test_pdfs.append(pdf_path)
    
    if len(test_pdfs) < 3:
        print(f"⚠️  Only {len(test_pdfs)} South of France PDFs found. Round 1B needs 3-10 documents.")
        print("Available PDFs:", [os.path.basename(p) for p in test_pdfs])
        
        # Try to find any PDFs
        all_pdfs = [f for f in os.listdir(parent_dir) if f.endswith('.pdf')]
        if len(all_pdfs) >= 3:
            print("Using available PDFs instead...")
            test_pdfs = [os.path.join(parent_dir, f) for f in all_pdfs[:5]]
        else:
            print("❌ Not enough PDFs found for testing")
            return
    
    print(f"📚 Testing with {len(test_pdfs)} PDFs")
    
    # Test different personas
    test_personas = [
        {
            "persona": "Travel Planner",
            "job_to_be_done": "Plan a 4-day trip for college friends"
        },
        {
            "persona": "Food Critic", 
            "job_to_be_done": "Write a restaurant review guide"
        }
    ]
    
    for test_case in test_personas:
        print(f"\n🎭 Testing Persona: {test_case['persona']}")
        print(f"🎯 Job: {test_case['job_to_be_done']}")
        print("-" * 50)
        
        try:
            start_time = time.time()
            
            # Initialize semantic ranker
            print("🔄 Loading models...")
            ranker = SemanticRanker(model_dir=models_dir)
            
            # Process each PDF and collect chunks
            all_chunks = []
            
            for pdf_path in test_pdfs:
                pdf_name = os.path.basename(pdf_path)
                print(f"📄 Processing: {pdf_name}")
                
                # Extract structure
                outline_data, doc = extract_document_structure(pdf_path)
                
                # Create chunks
                outline_json = json.dumps(outline_data, indent=2)
                chunks = create_semantic_chunks(pdf_path, outline_json)
                
                # Rank chunks for this document
                ranked = ranker.rank_chunks(chunks, test_case['persona'], test_case['job_to_be_done'])
                
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
            result = build_round1b_output([os.path.basename(p) for p in test_pdfs], test_case, top_chunks)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Validate output
            is_valid = validate_round1b_output(result)
            
            # Print results
            print(f"⏱️  Processing time: {processing_time:.2f} seconds")
            print(f"✅ Output format valid: {is_valid}")
            print(f"📊 Extracted sections: {len(result.get('extracted_sections', []))}")
            print(f"📝 Subsection analysis: {len(result.get('subsection_analysis', []))}")
            
            # Show top sections
            sections = result.get('extracted_sections', [])
            if sections:
                print("🏆 Top relevant sections:")
                for section in sections[:3]:
                    print(f"   {section['importance_rank']}. {section['section_title']} ({section['document']}, p{section['page_number']})")
            
            # Check constraints
            print(f"⚡ Time constraint (≤60s): {'✅ PASS' if processing_time <= 60 else '❌ FAIL'}")
            
            # Save test output
            persona_name = test_case['persona'].replace(' ', '_').lower()
            output_file = f"test_output_{persona_name}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"💾 Output saved to: {output_file}")
            
        except Exception as e:
            print(f"❌ Error testing persona '{test_case['persona']}': {str(e)}")
            import traceback
            traceback.print_exc()
            continue


def build_round1b_output(pdf_files, persona_config, top_chunks):
    """Build Round 1B output format."""
    
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
    
    return {
        "metadata": {
            "input_documents": pdf_files,
            "persona": persona_config["persona"],
            "job_to_be_done": persona_config["job_to_be_done"],
            "processing_timestamp": datetime.now().isoformat()
        },
        "extracted_sections": extracted_sections,
        "subsection_analysis": subsection_analysis
    }


def validate_round1b_output(result):
    """Validate Round 1B output format."""
    
    # Check required top-level keys
    required_keys = ['metadata', 'extracted_sections', 'subsection_analysis']
    if not all(key in result for key in required_keys):
        return False
    
    # Check metadata
    metadata = result['metadata']
    metadata_keys = ['input_documents', 'persona', 'job_to_be_done', 'processing_timestamp']
    if not all(key in metadata for key in metadata_keys):
        return False
    
    # Check extracted_sections
    sections = result['extracted_sections']
    if not isinstance(sections, list):
        return False
    
    for section in sections:
        section_keys = ['document', 'section_title', 'importance_rank', 'page_number']
        if not all(key in section for key in section_keys):
            return False
    
    # Check subsection_analysis
    analysis = result['subsection_analysis']
    if not isinstance(analysis, list):
        return False
    
    for item in analysis:
        analysis_keys = ['document', 'refined_text', 'page_number']
        if not all(key in item for key in analysis_keys):
            return False
    
    return True


if __name__ == "__main__":
    test_round1b()