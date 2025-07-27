#!/usr/bin/env python3
"""
Round 1A: Document Structure Extractor
Extracts title and heading outline from a single PDF document.
"""

import os
import sys
import json
from pdf_extractor_generic import extract_document_structure


def main():
    """Main entry point for Round 1A document structure extraction."""
    
    # Setup directories
    input_dir = "/app/input"
    output_dir = "/app/output"
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Find PDF file in input directory
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print("Error: No PDF files found in input directory")
        sys.exit(1)
    
    if len(pdf_files) > 1:
        print("Warning: Multiple PDF files found. Processing the first one.")
    
    pdf_path = os.path.join(input_dir, pdf_files[0])
    print(f"Processing: {pdf_files[0]}")
    
    try:
        # Extract document structure
        outline_data, doc = extract_document_structure(pdf_path)
        
        # Close document to free memory
        if doc:
            doc.close()
        
        # Save output
        output_path = os.path.join(output_dir, "document_structure.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(outline_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Document structure extracted successfully")
        print(f"📄 Title: {outline_data['title']}")
        print(f"📋 Headings found: {len(outline_data['outline'])}")
        print(f"💾 Output saved to: {output_path}")
        
        # Also print to stdout for verification
        print("\n" + "="*50)
        print("EXTRACTED STRUCTURE:")
        print("="*50)
        print(json.dumps(outline_data, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()