#!/usr/bin/env python3
"""
Local runner for Round 1A - Document Structure Extraction
Run this from the round1a directory to test with local PDFs
"""

import os
import sys
import json

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pdf_extractor_generic import extract_document_structure


def main():
    """Run Round 1A locally with PDFs from parent directory."""
    
    print("="*60)
    print("ROUND 1A: Document Structure Extraction (Local)")
    print("="*60)
    
    # Look for PDFs in parent directory
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    
    # Find available PDFs
    available_pdfs = []
    potential_pdfs = [
        "sample.pdf",
        "sample3.pdf",
        "South of France - Cities.pdf"
    ]
    
    for pdf_file in potential_pdfs:
        pdf_path = os.path.join(parent_dir, pdf_file)
        if os.path.exists(pdf_path):
            available_pdfs.append((pdf_file, pdf_path))
    
    if not available_pdfs:
        print("❌ No PDFs found in parent directory")
        print("Expected files: sample.pdf, sample1.pdf, or South of France PDFs")
        return
    
    # Let user choose which PDF to process
    print("Available PDFs:")
    for i, (name, _) in enumerate(available_pdfs, 1):
        print(f"  {i}. {name}")
    
    try:
        choice = input(f"\nSelect PDF to process (1-{len(available_pdfs)}) or press Enter for first: ").strip()
        if not choice:
            choice = "1"
        
        pdf_index = int(choice) - 1
        if pdf_index < 0 or pdf_index >= len(available_pdfs):
            print("Invalid choice, using first PDF")
            pdf_index = 0
            
    except ValueError:
        print("Invalid input, using first PDF")
        pdf_index = 0
    
    pdf_name, pdf_path = available_pdfs[pdf_index]
    
    print(f"\n📄 Processing: {pdf_name}")
    print("-" * 40)
    
    try:
        # Extract document structure
        result, doc = extract_document_structure(pdf_path)
        
        # Close document
        if doc:
            doc.close()
        
        # Display results
        print(f"✅ Processing completed successfully!")
        print(f"📋 Title: {result['title']}")
        print(f"📝 Headings found: {len(result['outline'])}")
        
        if result['outline']:
            print("\n📖 Document outline:")
            for heading in result['outline']:
                indent = "  " * (int(heading['level'][1]) - 1)  # H1=0, H2=1, H3=2 spaces
                print(f"{indent}{heading['level']}: {heading['text']} (Page {heading['page']})")
        
        # Save output
        output_file = f"output_{pdf_name.replace('.pdf', '.json')}"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Output saved to: {output_file}")
        
        # Show JSON output
        print(f"\n📄 JSON Output:")
        print("=" * 50)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"❌ Error processing {pdf_name}: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()