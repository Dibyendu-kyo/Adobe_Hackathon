"""
Improved PDF Document Structure Extractor for Round 1A
Enhanced to better match expected output format
"""

import fitz  # PyMuPDF
import re
from collections import Counter, defaultdict


def extract_document_structure(pdf_path):
    """
    Enhanced document structure extraction with improved title and heading detection.
    """
    doc = fitz.open(pdf_path)
    output = {"title": "Title Not Found", "outline": []}
    headings = []
    font_counts = Counter()
    page_texts = []
    
    # 1. Analyze document fonts and text patterns
    for page_num, page in enumerate(doc):
        text_dict = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
        page_texts.append(page.get_text())
        
        for block in text_dict.get("blocks", []):
            if block['type'] == 0:  # text block
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span['text'].strip()
                        if text and len(text) > 3:  # Only count substantial text
                            font_counts[(span['size'], span['font'])] += len(text)

    if not font_counts:
        doc.close()
        return output, None

    # Determine body text style (most common)
    body_text_style = font_counts.most_common(1)[0][0]
    body_text_size = body_text_style[0]
    
    # 2. Extract potential headings with enhanced filtering
    for page_num, page in enumerate(doc):
        text_dict = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
        mediabox = page.rect
        
        for block in text_dict.get("blocks", []):
            if block['type'] == 0:
                # Focus on single-line blocks for headings
                if len(block.get("lines", [])) == 1:
                    line = block["lines"][0]
                    line_text = "".join(s['text'] for s in line['spans']).strip()
                    
                    if not line_text or len(line_text) < 3:
                        continue
                    
                    span = line['spans'][0]
                    font_size = span['size']
                    font_name = span['font']
                    
                    # Enhanced heading detection criteria
                    is_larger = font_size > body_text_size + 1.0  # More strict size difference
                    is_bold = "bold" in font_name.lower() or "black" in font_name.lower() or (span['flags'] & 16)
                    is_reasonable_length = 5 <= len(line_text) <= 100  # Reasonable heading length
                    is_not_sentence = not line_text.endswith('.')
                    is_not_date = not re.match(r'^\w+\s\d{1,2},\s\d{4}', line_text)
                    is_numbered = bool(re.match(r'^(\d+\.?\s|\d+\.\d+\.?\s|[IVXLC]+\.?\s|[A-Z]\.?\s)', line_text))
                    is_title_case = line_text.istitle() or line_text.isupper()
                    
                    # Check for common heading patterns
                    heading_patterns = [
                        r'^(Chapter|Section|Part|Appendix)\s+\d+',
                        r'^\d+\.\s+\w+',
                        r'^\d+\.\d+\s+\w+',
                        r'^(Introduction|Overview|Conclusion|Summary|References)',
                        r'^(Table of Contents|Acknowledgements|Bibliography)',
                        r'^[A-Z][a-z]+(\s+[A-Z][a-z]+)*\s*$'
                    ]
                    
                    matches_pattern = any(re.match(pattern, line_text, re.IGNORECASE) for pattern in heading_patterns)
                    
                    # More selective heading criteria
                    if ((is_larger or is_bold or is_numbered or matches_pattern) and 
                        is_reasonable_length and is_not_sentence and is_not_date and
                        (is_title_case or is_numbered or matches_pattern)):
                        
                        headings.append({
                            'text': line_text,
                            'size': font_size,
                            'page': page_num + 1,
                            'is_numbered': is_numbered,
                            'is_bold': is_bold
                        })

    # 3. Enhanced title extraction
    title = None
    
    # Try PDF metadata first
    try:
        meta = doc.metadata
        if meta and meta.get('title') and meta['title'].strip().lower() != 'untitled':
            title = meta['title'].strip()
            # Clean up title - remove file extensions and extra info
            title = re.sub(r'\.(pdf|doc|docx)$', '', title, flags=re.IGNORECASE)
            title = re.sub(r'\s+v\d+.*$', '', title)  # Remove version info
            title = re.sub(r'\s+\d{8}.*$', '', title)  # Remove date codes
    except Exception:
        pass
    
    # If no good metadata title, look for document title in first few pages
    if not title or len(title) < 5:
        # Look for largest heading on first 2 pages that looks like a title
        title_candidates = [h for h in headings if h['page'] <= 2 and not h['is_numbered']]
        if title_candidates:
            # Prefer larger, non-numbered headings
            title_candidates.sort(key=lambda x: (-x['size'], x['page']))
            potential_title = title_candidates[0]['text']
            
            # Clean up potential title
            if len(potential_title) <= 80 and not potential_title.lower().startswith(('table of', 'revision', 'acknowledgement')):
                title = potential_title
    
    # Final title cleanup
    if title:
        title = re.sub(r'\s+', ' ', title).strip()  # Normalize whitespace
        if title.endswith(' '):
            title = title.rstrip()
    
    output['title'] = title if title else "Title Not Found"

    # 4. Enhanced heading level assignment
    if headings:
        # Sort headings by page and position
        headings.sort(key=lambda x: (x['page'], -x['size']))
        
        # Group by font size for level assignment
        size_groups = {}
        for h in headings:
            size = round(h['size'], 1)  # Round to avoid floating point issues
            if size not in size_groups:
                size_groups[size] = []
            size_groups[size].append(h)
        
        # Sort sizes in descending order
        sorted_sizes = sorted(size_groups.keys(), reverse=True)
        
        # Assign levels more intelligently
        level_map = {}
        level_counter = 1
        
        for size in sorted_sizes:
            if level_counter == 1:
                level_map[size] = "H1"
            elif level_counter == 2:
                level_map[size] = "H2"
            else:
                level_map[size] = "H3"
            level_counter += 1
            if level_counter > 3:  # Only H1, H2, H3
                level_map[size] = "H3"
        
        # Build final outline
        for h in headings:
            size = round(h['size'], 1)
            level = level_map.get(size, "H3")
            
            # Additional filtering for final output
            text = h['text'].strip()
            if len(text) >= 3 and len(text) <= 100:  # Reasonable length
                output['outline'].append({
                    "level": level,
                    "text": text,
                    "page": h['page']
                })

    return output, doc


# Backward compatibility - use improved version by default
if __name__ == "__main__":
    # Test with a sample PDF
    import sys
    if len(sys.argv) > 1:
        result, doc = extract_document_structure(sys.argv[1])
        if doc:
            doc.close()
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))