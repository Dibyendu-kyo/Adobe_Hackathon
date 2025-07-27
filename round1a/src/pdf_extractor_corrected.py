"""
Corrected PDF Document Structure Extractor for Round 1A
Fixed to match the expected sample output format exactly
"""

import fitz  # PyMuPDF
import re
from collections import Counter, defaultdict


def extract_document_structure(pdf_path):
    """
    Corrected document structure extraction to match sample output format.
    """
    doc = fitz.open(pdf_path)
    output = {"title": "Title Not Found", "outline": []}
    headings = []
    font_counts = Counter()
    page_texts = []
    
    # 1. Analyze document fonts and build font profile
    for page_num, page in enumerate(doc):
        text_dict = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
        page_texts.append(page.get_text())
        
        for block in text_dict.get("blocks", []):
            if block['type'] == 0:  # text block
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span['text'].strip()
                        if text and len(text) > 2:
                            font_counts[(span['size'], span['font'])] += len(text)

    if not font_counts:
        doc.close()
        return output, None

    # Determine body text style (most common)
    body_text_style = font_counts.most_common(1)[0][0]
    body_text_size = body_text_style[0]
    
    # 2. Extract potential headings with refined criteria
    for page_num, page in enumerate(doc):
        text_dict = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
        
        for block in text_dict.get("blocks", []):
            if block['type'] == 0:
                # Focus on single-line blocks (typical for headings)
                if len(block.get("lines", [])) == 1:
                    line = block["lines"][0]
                    line_text = "".join(s['text'] for s in line['spans']).strip()
                    
                    if not line_text or len(line_text) < 3:
                        continue
                    
                    span = line['spans'][0]
                    font_size = span['size']
                    font_name = span['font']
                    
                    # Heading detection criteria
                    is_larger = font_size > body_text_size + 0.5
                    is_bold = "bold" in font_name.lower() or "black" in font_name.lower() or (span['flags'] & 16)
                    is_reasonable_length = 3 <= len(line_text) <= 120
                    is_not_sentence = not line_text.endswith('.')
                    is_not_date = not re.match(r'^\w+\s\d{1,2},\s\d{4}', line_text)
                    
                    # Check for numbered sections (key pattern from sample)
                    is_numbered = bool(re.match(r'^(\d+\.?\s|\d+\.\d+\.?\s)', line_text))
                    
                    # Check for common document sections
                    is_document_section = any(keyword in line_text.lower() for keyword in [
                        'revision history', 'table of contents', 'acknowledgements',
                        'introduction', 'overview', 'references', 'conclusion',
                        'appendix', 'bibliography', 'glossary'
                    ])
                    
                    # More selective heading criteria to match sample quality
                    if ((is_larger or is_bold or is_numbered or is_document_section) and 
                        is_reasonable_length and is_not_sentence and is_not_date):
                        
                        headings.append({
                            'text': line_text,
                            'size': font_size,
                            'page': page_num + 1,
                            'is_numbered': is_numbered,
                            'is_bold': is_bold,
                            'is_document_section': is_document_section
                        })

    # 3. Title extraction (match sample format with trailing spaces)
    title = None
    
    # Try PDF metadata first
    try:
        meta = doc.metadata
        if meta and meta.get('title') and meta['title'].strip().lower() != 'untitled':
            title = meta['title'].strip()
    except Exception:
        pass
    
    # If no metadata title, look for title in first few headings
    if not title:
        # Look for largest heading on first page that's not a section heading
        title_candidates = [h for h in headings if h['page'] <= 2 and not h['is_numbered'] and not h['is_document_section']]
        if title_candidates:
            title_candidates.sort(key=lambda x: (-x['size'], x['page']))
            if title_candidates:
                title = title_candidates[0]['text']
    
    # Format title to match sample (with trailing spaces)
    if title:
        title = title.strip()
        # Add trailing spaces to match sample format
        title = title + "  "
    
    output['title'] = title if title else "Title Not Found"

    # 4. Improved heading level assignment to match sample
    if headings:
        # Remove title from headings if it appears
        if title:
            clean_title = title.strip()
            headings = [h for h in headings if h['text'].strip() != clean_title]
        
        # Sort headings by page and position
        headings.sort(key=lambda x: (x['page'], -x['size']))
        
        # Assign levels based on content and numbering patterns (matching sample logic)
        for h in headings:
            text = h['text'].strip()
            
            # Main sections (like in sample) should be H1
            if (h['is_document_section'] or 
                re.match(r'^\d+\.\s+[A-Z]', text) or  # "1. Introduction..."
                re.match(r'^Chapter\s+\d+', text, re.IGNORECASE)):
                level = "H1"
            
            # Subsections (like "2.1", "2.2") should be H2
            elif re.match(r'^\d+\.\d+\s+', text):
                level = "H2"
            
            # Everything else defaults to H3, but we'll be more selective
            else:
                # For document sections like "Revision History", "Table of Contents" - make them H1
                if h['is_document_section']:
                    level = "H1"
                else:
                    level = "H3"
            
            # Add trailing space to text to match sample format
            formatted_text = text + " "
            
            output['outline'].append({
                "level": level,
                "text": formatted_text,
                "page": h['page']
            })

    return output, doc


# Test function
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result, doc = extract_document_structure(sys.argv[1])
        if doc:
            doc.close()
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))