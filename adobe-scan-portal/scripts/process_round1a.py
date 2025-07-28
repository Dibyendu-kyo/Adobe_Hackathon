#!/usr/bin/env python3
"""
Standalone script for Round 1A processing
Called from the Next.js API route
"""

import sys
import os
import json
import gc
import time
from contextlib import contextmanager

# Add the round1a src to path
script_dir = os.path.dirname(os.path.abspath(__file__))
round1a_src = os.path.join(script_dir, '..', '..', 'round1a', 'src')
sys.path.append(round1a_src)

@contextmanager
def performance_timer(operation_name):
    """Context manager for timing operations"""
    start_time = time.time()
    try:
        yield
    finally:
        elapsed = time.time() - start_time
        print(f"DEBUG: {operation_name} took {elapsed:.2f} seconds", file=sys.stderr)

def main():
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: python process_round1a.py <pdf_file>"}), file=sys.stderr)
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if not os.path.exists(pdf_path):
        print(json.dumps({"error": f"File not found: {pdf_path}"}), file=sys.stderr)
        sys.exit(1)
    
    try:
        # Check file size
        file_size = os.path.getsize(pdf_path)
        if file_size > 50 * 1024 * 1024:  # 50MB limit
            print(json.dumps({"error": "File too large. Maximum size is 50MB"}), file=sys.stderr)
            sys.exit(1)
        
        # Import with error handling
        try:
            from pdf_extractor_generic import extract_document_structure
        except ImportError as e:
            print(json.dumps({"error": f"Failed to import extractor: {e}"}), file=sys.stderr)
            sys.exit(1)
        
        # Extract document structure with timing
        with performance_timer("PDF extraction"):
            result, doc = extract_document_structure(pdf_path)
        
        # Close document to free memory
        if doc:
            doc.close()
        
        # Force garbage collection
        gc.collect()
        
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
        
        with performance_timer("Text cleaning"):
            cleaned_result = clean_text(result)
        
        # Validate result structure
        if not isinstance(cleaned_result, dict):
            print(json.dumps({"error": "Invalid result structure"}), file=sys.stderr)
            sys.exit(1)
        
        if 'title' not in cleaned_result or 'outline' not in cleaned_result:
            print(json.dumps({"error": "Missing required fields in result"}), file=sys.stderr)
            sys.exit(1)
        
        # Output result as JSON with ASCII encoding to avoid Unicode issues
        print(json.dumps(cleaned_result, ensure_ascii=True, indent=None))
        
    except MemoryError:
        print(json.dumps({"error": "Insufficient memory to process file"}), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": f"Processing failed: {str(e)}"}), file=sys.stderr)
        sys.exit(1)
    finally:
        # Final garbage collection
        gc.collect()

if __name__ == "__main__":
    main()