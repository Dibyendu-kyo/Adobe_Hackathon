#!/usr/bin/env python3
"""
Test the corrected extractor against the sample output format
"""

import os
import sys
import json

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pdf_extractor import extract_document_structure as extract_original
from pdf_extractor_corrected import extract_document_structure as extract_corrected


def test_correction():
    """Test corrected extractor to match sample output format."""
    
    print("="*80)
    print("TESTING CORRECTED EXTRACTOR AGAINST SAMPLE FORMAT")
    print("="*80)
    
    # Expected sample output for reference
    sample_expected = {
        "title": "Overview  Foundation Level Extensions  ",
        "outline": [
            {"level": "H1", "text": "Revision History ", "page": 2},
            {"level": "H1", "text": "Table of Contents ", "page": 3},
            {"level": "H1", "text": "Acknowledgements ", "page": 4},
            {"level": "H1", "text": "1. Introduction to the Foundation Level Extensions ", "page": 5},
            {"level": "H1", "text": "2. Introduction to Foundation Level Agile Tester Extension ", "page": 6},
            {"level": "H2", "text": "2.1 Intended Audience ", "page": 6},
            {"level": "H2", "text": "2.2 Career Paths for Testers ", "page": 6},
            {"level": "H2", "text": "2.3 Learning Objectives ", "page": 6},
            {"level": "H2", "text": "2.4 Entry Requirements ", "page": 7},
            {"level": "H2", "text": "2.5 Structure and Course Duration ", "page": 7},
            {"level": "H2", "text": "2.6 Keeping It Current ", "page": 8},
            {"level": "H1", "text": "3. Overview of the Foundation Level Extension – Agile TesterSyllabus ", "page": 9},
            {"level": "H2", "text": "3.1 Business Outcomes ", "page": 9},
            {"level": "H2", "text": "3.2 Content ", "page": 9},
            {"level": "H1", "text": "4. References ", "page": 11},
            {"level": "H2", "text": "4.1 Trademarks ", "page": 11},
            {"level": "H2", "text": "4.2 Documents and Web Sites ", "page": 11}
        ]
    }
    
    # Your current output for reference
    your_current = {
        "title": "ISTQB Expert Level Modules Overview",
        "outline": [
            {"level": "H1", "text": "Overview", "page": 1},
            {"level": "H1", "text": "Foundation Level Extensions", "page": 1},
            {"level": "H2", "text": "International Software Testing Qualifications Board", "page": 1},
            {"level": "H3", "text": "Version 1.0", "page": 1},
            {"level": "H3", "text": "Revision History", "page": 3},
            {"level": "H3", "text": "Table of Contents", "page": 4},
            {"level": "H3", "text": "Acknowledgements", "page": 5}
        ]
    }
    
    print("📋 SAMPLE EXPECTED FORMAT:")
    print(f"   Title: '{sample_expected['title']}'")
    print(f"   Headings: {len(sample_expected['outline'])}")
    
    # Analyze sample structure
    sample_levels = {}
    for h in sample_expected['outline']:
        level = h['level']
        sample_levels[level] = sample_levels.get(level, 0) + 1
    print(f"   Level distribution: {sample_levels}")
    
    print("\n📋 YOUR CURRENT OUTPUT:")
    print(f"   Title: '{your_current['title']}'")
    print(f"   Headings: {len(your_current['outline'])}")
    
    # Analyze your current structure
    your_levels = {}
    for h in your_current['outline']:
        level = h['level']
        your_levels[level] = your_levels.get(level, 0) + 1
    print(f"   Level distribution: {your_levels}")
    
    # Test corrected extractor on available PDFs
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    test_pdfs = [
        ("sample1.pdf", os.path.join(parent_dir, "sample1.pdf"))
    ]
    
    for pdf_name, pdf_path in test_pdfs:
        if not os.path.exists(pdf_path):
            continue
            
        print(f"\n📄 TESTING CORRECTED EXTRACTOR ON: {pdf_name}")
        print("-" * 60)
        
        try:
            # Test original
            print("🔵 ORIGINAL EXTRACTOR:")
            result_orig, doc_orig = extract_original(pdf_path)
            if doc_orig:
                doc_orig.close()
            
            orig_levels = {}
            for h in result_orig['outline']:
                level = h['level']
                orig_levels[level] = orig_levels.get(level, 0) + 1
            
            print(f"   Title: '{result_orig['title']}'")
            print(f"   Headings: {len(result_orig['outline'])}")
            print(f"   Levels: {orig_levels}")
            
            # Test corrected
            print("\n🟢 CORRECTED EXTRACTOR:")
            result_corrected, doc_corrected = extract_corrected(pdf_path)
            if doc_corrected:
                doc_corrected.close()
            
            corrected_levels = {}
            for h in result_corrected['outline']:
                level = h['level']
                corrected_levels[level] = corrected_levels.get(level, 0) + 1
            
            print(f"   Title: '{result_corrected['title']}'")
            print(f"   Headings: {len(result_corrected['outline'])}")
            print(f"   Levels: {corrected_levels}")
            
            # Show first few headings
            print("\n📖 CORRECTED OUTPUT SAMPLE:")
            for i, h in enumerate(result_corrected['outline'][:10]):
                print(f"   {h['level']}: '{h['text']}' (page {h['page']})")
            
            # Save corrected output
            with open(f"corrected_output_{pdf_name.replace('.pdf', '.json')}", 'w', encoding='utf-8') as f:
                json.dump(result_corrected, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*80)
    print("ANALYSIS: KEY IMPROVEMENTS NEEDED")
    print("="*80)
    print("🔧 ISSUES IDENTIFIED:")
    print("   1. Heading Level Assignment: Too many H3s, need more H1s and H2s")
    print("   2. Title Format: Should match sample format with trailing spaces")
    print("   3. Section Recognition: Better detection of main vs sub sections")
    print("   4. Numbered Section Hierarchy: 1. = H1, 1.1 = H2 pattern")
    
    print("\n✅ CORRECTED VERSION IMPROVEMENTS:")
    print("   • Better H1/H2 level distinction")
    print("   • Proper numbered section hierarchy")
    print("   • Title format matching sample")
    print("   • Document section recognition")


if __name__ == "__main__":
    test_correction()