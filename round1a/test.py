#!/usr/bin/env python3
"""
Test script for Round 1A - Document Structure Extraction
Run from round1a directory: python test.py
"""

import os
import sys
import json
import time

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pdf_extractor_generic import extract_document_structure


def test_round1a():
    """Test Round 1A implementation with sample PDFs."""
    
    print("="*60)
    print("TESTING ROUND 1A: Document Structure Extraction")
    print("="*60)
    
    # Look for PDFs in parent directory and current directory
    test_pdfs = []
    
    # Check parent directory for sample PDFs
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    potential_pdfs = [
        "sample.pdf",
        "sample1.pdf", 
        "South of France - Cities.pdf"
    ]
    
    for pdf_file in potential_pdfs:
        parent_path = os.path.join(parent_dir, pdf_file)
        if os.path.exists(parent_path):
            test_pdfs.append(parent_path)
    
    # Check current directory
    for pdf_file in potential_pdfs:
        if os.path.exists(pdf_file):
            test_pdfs.append(pdf_file)
    
    if not test_pdfs:
        print("❌ No test PDFs found. Please ensure sample PDFs are available.")
        print("Expected files: sample.pdf, sample1.pdf, or South of France PDFs")
        return
    
    for pdf_path in test_pdfs:
        pdf_name = os.path.basename(pdf_path)
        print(f"\n📄 Testing: {pdf_name}")
        print("-" * 40)
        
        try:
            # Measure processing time
            start_time = time.time()
            
            # Extract document structure
            result, doc = extract_document_structure(pdf_path)
            
            # Close document
            if doc:
                doc.close()
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Validate output format
            is_valid = validate_round1a_output(result)
            
            # Print results
            print(f"⏱️  Processing time: {processing_time:.2f} seconds")
            print(f"✅ Output format valid: {is_valid}")
            print(f"📋 Title: {result.get('title', 'N/A')}")
            print(f"📝 Headings found: {len(result.get('outline', []))}")
            
            # Show first few headings
            outline = result.get('outline', [])
            if outline:
                print("📖 Sample headings:")
                for i, heading in enumerate(outline[:3]):
                    print(f"   {heading['level']}: {heading['text']} (Page {heading['page']})")
                if len(outline) > 3:
                    print(f"   ... and {len(outline) - 3} more")
            
            # Check constraints
            print(f"⚡ Time constraint (≤10s): {'✅ PASS' if processing_time <= 10 else '❌ FAIL'}")
            
            # Save test output
            output_file = f"test_output_{pdf_name.replace('.pdf', '.json')}"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"💾 Output saved to: {output_file}")
            
        except Exception as e:
            print(f"❌ Error processing {pdf_name}: {str(e)}")
            import traceback
            traceback.print_exc()
            continue


def validate_round1a_output(result):
    """Validate Round 1A output format."""
    
    # Check required keys
    if not isinstance(result, dict):
        return False
    
    if 'title' not in result or 'outline' not in result:
        return False
    
    # Check title
    if not isinstance(result['title'], str):
        return False
    
    # Check outline
    outline = result['outline']
    if not isinstance(outline, list):
        return False
    
    # Check each heading
    for heading in outline:
        if not isinstance(heading, dict):
            return False
        
        required_keys = ['level', 'text', 'page']
        if not all(key in heading for key in required_keys):
            return False
        
        # Check level is H1, H2, or H3
        if heading['level'] not in ['H1', 'H2', 'H3']:
            return False
        
        # Check text is string
        if not isinstance(heading['text'], str):
            return False
        
        # Check page is positive integer
        if not isinstance(heading['page'], int) or heading['page'] < 1:
            return False
    
    return True


if __name__ == "__main__":
    test_round1a()