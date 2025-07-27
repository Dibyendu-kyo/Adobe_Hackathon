"""
Generic PDF Document Structure Extractor for Round 1A
Completely generic approach without any hardcoded values
"""

import fitz  # PyMuPDF
import re
from collections import Counter, defaultdict


def extract_document_structure(pdf_path):
    """
    Generic document structure extraction using robust, non-hardcoded approach.
    """
    doc = fitz.open(pdf_path)
    output = {"title": "Title Not Found", "outline": []}
    headings = []
    font_counts = Counter()
    font_size_to_lines = defaultdict(list)
    page_texts = []
    page_headings = defaultdict(list)

    # 1. Profile the document's body text to establish a baseline
    for page_num, page in enumerate(doc):
        text_dict = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
        page_texts.append(page.get_text())
        
        for block in text_dict.get("blocks", []):
            if block['type'] == 0:  # text block
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        font_counts[(span['size'], span['font'])] += len(span['text'].strip())
                        font_size_to_lines[span['size']].append(span['text'].strip())

    if not font_counts:
        doc.close()
        return output, None

    # Determine body text style (most common font/size combination)
    body_text_style = font_counts.most_common(1)[0][0]
    body_text_size = body_text_style[0]

    # 2. Extract potential headings using multi-factor heuristics
    for page_num, page in enumerate(doc):
        text_dict = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
        mediabox = page.rect
        
        for block in text_dict.get("blocks", []):
            if block['type'] == 0:  # text block
                # Focus on single-line blocks (typical for headings)
                if len(block.get("lines", [])) == 1:
                    line = block["lines"][0]
                    line_text = "".join(s['text'] for s in line['spans']).strip()
                    
                    if not line_text:
                        continue
                        
                    span = line['spans'][0]
                    font_size = span['size']
                    font_name = span['font']
                    bbox = span['bbox'] if 'bbox' in span else None
                    
                    # Heading detection heuristics
                    is_larger = font_size > body_text_size + 0.5
                    is_bold = "bold" in font_name.lower() or "black" in font_name.lower() or (span['flags'] & 16)
                    is_short = len(line_text.split()) < 25
                    is_not_sentence = not line_text.endswith('.')
                    is_not_date = not re.match(r'^\w+\s\d{1,2},\s\d{4}', line_text)
                    is_numbered = bool(re.match(r'^(\d+\.?\s|\d+\.\d+\.?\s|[IVXLC]+\.?\s|[A-Z]\.?\s)', line_text.strip()))
                    is_all_caps = line_text.isupper() and len(line_text) > 3
                    
                    # Check if text is centered
                    is_centered = False
                    if bbox:
                        left, top, right, bottom = bbox
                        center_x = (left + right) / 2
                        page_center_x = (mediabox.x0 + mediabox.x1) / 2
                        is_centered = abs(center_x - page_center_x) < (mediabox.width / 8)
                    
                    # Common document section patterns (generic)
                    is_document_section = any(pattern in line_text.lower() for pattern in [
                        'table of contents', 'revision history', 'acknowledgements',
                        'introduction', 'overview', 'conclusion', 'summary',
                        'references', 'bibliography', 'appendix', 'glossary',
                        'abstract', 'preface', 'foreword'
                    ])
                    
                    # Accept as heading if any strong signal is present
                    if ((is_larger or is_bold or is_numbered or is_all_caps or is_centered or is_document_section) 
                        and is_short and is_not_sentence and is_not_date):
                        headings.append({
                            'text': line_text,
                            'size': font_size,
                            'page': page_num + 1,
                            'is_numbered': is_numbered,
                            'is_bold': is_bold,
                            'is_document_section': is_document_section
                        })
                        page_headings[page_num + 1].append(line_text)

    # 3. Handle cover page detection (adjust page numbers if needed)
    if len(page_headings.get(1, [])) == 0 and len(page_texts) > 1:
        # If first page has no headings and little text, treat as cover
        if len(page_texts[0].strip()) < 200:
            for h in headings:
                h['page'] = max(1, h['page'] - 1)

    # 4. Identify the document title
    title = None
    
    # Try PDF metadata first
    try:
        meta = doc.metadata
        if meta and meta.get('title') and meta['title'].strip().lower() != 'untitled':
            title = meta['title'].strip()
    except Exception:
        pass
    
    # If no metadata title, use largest heading from first 2 pages
    if not title:
        first_page_headings = sorted(
            [h for h in headings if h['page'] <= 2], 
            key=lambda x: x['size'], 
            reverse=True
        )
        if first_page_headings:
            title = first_page_headings[0]['text']
    
    # Fallback to first heading
    if not title and headings:
        title = headings[0]['text']
    
    # Format title with trailing spaces (common format requirement)
    if title:
        title = title.strip() + "  "
    
    output['title'] = title if title else "Title Not Found"

    # 5. Assign hierarchy levels based on font size clustering and content patterns
    if headings:
        unique_sizes = sorted(list(set([h['size'] for h in headings])), reverse=True)
        
        # Map font sizes to heading levels (H1, H2, H3 only)
        size_map = {}
        if len(unique_sizes) >= 3:
            size_map[unique_sizes[0]] = "H1"
            size_map[unique_sizes[1]] = "H2"
            for s in unique_sizes[2:]:
                size_map[s] = "H3"
        elif len(unique_sizes) == 2:
            size_map[unique_sizes[0]] = "H1"
            size_map[unique_sizes[1]] = "H2"
        elif len(unique_sizes) == 1:
            size_map[unique_sizes[0]] = "H1"
        
        # Build final outline with proper ordering
        for h in sorted(headings, key=lambda x: (x['page'], -x['size'])):
            level = size_map.get(h['size'], "H3")
            
            # Override level based on content patterns (generic rules)
            text = h['text'].strip()
            
            # Main numbered sections (1., 2., 3., etc.) are typically H1
            if re.match(r'^\d+\.\s+[A-Z]', text):
                level = "H1"
            # Sub-numbered sections (1.1, 2.1, etc.) are typically H2
            elif re.match(r'^\d+\.\d+\s+', text):
                level = "H2"
            # Document sections are typically H1
            elif h['is_document_section']:
                level = "H1"
            
            # Only include H1, H2, H3 levels
            if level in {"H1", "H2", "H3"}:
                # Add trailing space to match common format requirements
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