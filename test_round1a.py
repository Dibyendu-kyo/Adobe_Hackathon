#!/usr/bin/env python3
"""
Test script for Round 1A - Document Structure Extraction
"""

import os
import sys
import json
import time
from round1a.src.pdf_extractor import extract_document_structure


def test_round1a():
    """Test Round 1A implementation with sample PDFs."""
    
    print("="*60)
    print("TESTING ROUND 1A: Document Structure Extraction")
    print("="*60)
    
    # Test with available sample PDFs
    test_pdfs = [
        "sample.pdf",
        "sample1.pdf", 
        "South of France - Cities.pdf"
    ]
    
    for pdf_file in test_pdfs:
        if not os.path.exists(pdf_file):
            print(f"⚠️  Skipping {pdf_file} - file not found")
            continue
            
        print(f"\n📄 Testing: {pdf_file}")
        print("-" * 40)
        
        try:
            # Measure processing time
            start_time = time.time()
            
            # Extract document structure
            result, doc = extract_document_structure(pdf_file)
            
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
            output_file = f"test_output_1a_{os.path.basename(pdf_file).replace('.pdf', '.json')}"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"💾 Output saved to: {output_file}")
            
        except Exception as e:
            print(f"❌ Error processing {pdf_file}: {str(e)}")
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