#!/usr/bin/env python3
"""
Standalone script for Round 1A processing
Called from the Next.js API route
"""

import sys
import os
import json

# Add the round1a src to path
script_dir = os.path.dirname(os.path.abspath(__file__))
round1a_src = os.path.join(script_dir, '..', '..', 'round1a', 'src')
sys.path.append(round1a_src)

try:
    from pdf_extractor_generic import extract_document_structure
except ImportError as e:
    print(json.dumps({"error": f"Failed to import extractor: {e}"}), file=sys.stderr)
    sys.exit(1)

def main():
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: python process_round1a.py <pdf_file>"}), file=sys.stderr)
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if not os.path.exists(pdf_path):
        print(json.dumps({"error": f"File not found: {pdf_path}"}), file=sys.stderr)
        sys.exit(1)
    
    try:
        # Extract document structure
        result, doc = extract_document_structure(pdf_path)
        
        # Close document to free memory
        if doc:
            doc.close()
        
        # Clean the result to remove problematic Unicode characters
        def clean_text(obj):
            if isinstance(obj, str):
                # Replace problematic Unicode characters
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