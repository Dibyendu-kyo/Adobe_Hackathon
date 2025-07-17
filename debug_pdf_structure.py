import fitz
from collections import Counter

def debug_pdf_structure(pdf_path):
    """Debug PDF structure to understand why no headings are found"""
    doc = fitz.open(pdf_path)
    
    print(f"Analyzing PDF: {pdf_path}")
    print(f"Total pages: {len(doc)}")
    
    # Analyze fonts
    font_counts = Counter()
    all_text_samples = []
    
    for page_num, page in enumerate(doc):
        print(f"\n--- Page {page_num + 1} ---")
        text_dict = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
        
        page_fonts = set()
        page_text_samples = []
        
        for block in text_dict.get("blocks", []):
            if block['type'] == 0:  # text block
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span['text'].strip()
                        if text:
                            font_key = (span['size'], span['font'])
                            font_counts[font_key] += len(text)
                            page_fonts.add(font_key)
                            
                            # Collect text samples
                            if len(text) > 5 and len(text) < 100:
                                page_text_samples.append({
                                    'text': text,
                                    'size': span['size'],
                                    'font': span['font'],
                                    'flags': span.get('flags', 0)
                                })
        
        print(f"Fonts found on page: {len(page_fonts)}")
        for font in sorted(page_fonts, key=lambda x: x[0], reverse=True)[:5]:
            print(f"  Size {font[0]:.1f}: {font[1]}")
        
        # Show some text samples
        print("Text samples:")
        for sample in page_text_samples[:10]:
            is_bold = "bold" in sample['font'].lower() or (sample['flags'] & 16)
            bold_marker = " [BOLD]" if is_bold else ""
            print(f"  Size {sample['size']:.1f}: '{sample['text'][:50]}...'{bold_marker}")
        
        if page_num >= 2:  # Only analyze first 3 pages
            break
    
    print(f"\n--- Font Analysis ---")
    print("Most common fonts (likely body text):")
    for i, (font_key, count) in enumerate(font_counts.most_common(10)):
        print(f"{i+1}. Size {font_key[0]:.1f}, Font: {font_key[1]}, Count: {count}")
    
    if font_counts:
        body_font = font_counts.most_common(1)[0][0]
        body_size = body_font[0]
        print(f"\nBody text size: {body_size:.1f}")
        
        # Look for potential headings
        print("\nPotential headings (larger than body text):")
        potential_headings = []
        
        for page_num, page in enumerate(doc):
            text_dict = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
            for block in text_dict.get("blocks", []):
                if block['type'] == 0 and len(block.get("lines", [])) == 1:
                    line = block["lines"][0]
                    line_text = "".join(s['text'] for s in line['spans']).strip()
                    if line_text and len(line_text) > 3:
                        span = line['spans'][0]
                        font_size = span['size']
                        font_name = span['font']
                        
                        if font_size > body_size + 0.5:  # Slightly larger threshold
                            is_bold = "bold" in font_name.lower() or (span['flags'] & 16)
                            potential_headings.append({
                                'text': line_text,
                                'size': font_size,
                                'page': page_num + 1,
                                'bold': is_bold,
                                'font': font_name
                            })
        
        for heading in potential_headings[:15]:
            bold_marker = " [BOLD]" if heading['bold'] else ""
            print(f"  Page {heading['page']}, Size {heading['size']:.1f}: '{heading['text'][:60]}...'{bold_marker}")
    
    doc.close()

if __name__ == "__main__":
    debug_pdf_structure("sample4.pdf")