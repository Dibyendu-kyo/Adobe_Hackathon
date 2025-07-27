#!/usr/bin/env python3
"""
Compare original vs improved PDF extractor
"""

import os
import sys
import json

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pdf_extractor import extract_document_structure as extract_original
from pdf_extractor_improved import extract_document_structure as extract_improved


def compare_extractors():
    """Compare original vs improved extractor on available PDFs."""
    
    print("="*80)
    print("COMPARING ORIGINAL VS IMPROVED PDF EXTRACTORS")
    print("="*80)
    
    # Find test PDFs
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    test_pdfs = []
    
    potential_pdfs = [
        "sample.pdf",
        "sample1.pdf",
        "South of France - Cities.pdf"
    ]
    
    for pdf_file in potential_pdfs:
        pdf_path = os.path.join(parent_dir, pdf_file)
        if os.path.exists(pdf_path):
            test_pdfs.append((pdf_file, pdf_path))
    
    if not test_pdfs:
        print("❌ No test PDFs found")
        return
    
    for pdf_name, pdf_path in test_pdfs:
        print(f"\n📄 TESTING: {pdf_name}")
        print("="*60)
        
        try:
            # Test original extractor
            print("🔵 ORIGINAL EXTRACTOR:")
            result_orig, doc_orig = extract_original(pdf_path)
            if doc_orig:
                doc_orig.close()
            
            print(f"   Title: {result_orig['title']}")
            print(f"   Headings: {len(result_orig['outline'])}")
            
            # Show heading levels distribution
            levels_orig = {}
            for h in result_orig['outline']:
                level = h['level']
                levels_orig[level] = levels_orig.get(level, 0) + 1
            print(f"   Levels: {dict(levels_orig)}")
            
            # Test improved extractor
            print("\n🟢 IMPROVED EXTRACTOR:")
            result_improved, doc_improved = extract_improved(pdf_path)
            if doc_improved:
                doc_improved.close()
            
            print(f"   Title: {result_improved['title']}")
            print(f"   Headings: {len(result_improved['outline'])}")
            
            # Show heading levels distribution
            levels_improved = {}
            for h in result_improved['outline']:
                level = h['level']
                levels_improved[level] = levels_improved.get(level, 0) + 1
            print(f"   Levels: {dict(levels_improved)}")
            
            # Show first few headings from each
            print("\n📋 COMPARISON OF FIRST 5 HEADINGS:")
            print("   Original:")
            for i, h in enumerate(result_orig['outline'][:5]):
                print(f"     {h['level']}: {h['text']} (p{h['page']})")
            
            print("   Improved:")
            for i, h in enumerate(result_improved['outline'][:5]):
                print(f"     {h['level']}: {h['text']} (p{h['page']})")
            
            # Save both outputs for comparison
            with open(f"comparison_original_{pdf_name.replace('.pdf', '.json')}", 'w', encoding='utf-8') as f:
                json.dump(result_orig, f, indent=2, ensure_ascii=False)
            
            with open(f"comparison_improved_{pdf_name.replace('.pdf', '.json')}", 'w', encoding='utf-8') as f:
                json.dump(result_improved, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            print(f"❌ Error processing {pdf_name}: {str(e)}")
            continue
    
    print(f"\n✅ Comparison complete! Check comparison_*.json files for detailed results.")


if __name__ == "__main__":
    compare_extractors()