import os
import json
import fitz  # PyMuPDF

def create_semantic_chunks(pdf_path, outline_json):
    # Load outline from JSON string
    outline_data = json.loads(outline_json)
    outline = outline_data.get('outline', [])

    # Extract doc name from file name
    doc_name = os.path.basename(pdf_path)

    # Get full text from PDF using simple extraction
    document = fitz.open(pdf_path)
    full_text_by_page = {}
    
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        page_text = page.get_text()
        full_text_by_page[page_num + 1] = page_text
    
    document.close()

    # Create chunks based on outline structure
    chunks = []
    
    for i, heading in enumerate(outline):
        section_title = heading['text']
        page_num = heading['page']
        
        # Get text content for this section
        # For simplicity, use text from the page where the heading appears
        page_text = full_text_by_page.get(page_num, '')
        
        # Try to extract content after the heading
        lines = page_text.split('\n')
        content_lines = []
        found_heading = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for the heading in the text
            if section_title.lower() in line.lower() and not found_heading:
                found_heading = True
                continue
            
            # Collect content after heading until next major section
            if found_heading:
                # Stop at next major heading or if line looks like a heading
                if (line.isupper() and len(line.split()) <= 8) or \
                   line.startswith(('Appendix', 'Phase', 'Summary', 'Background')):
                    break
                content_lines.append(line)
        
        # If no specific content found, use some page text
        if not content_lines and page_text:
            content_lines = page_text.split('\n')[:10]  # First 10 lines
        
        chunk_text = ' '.join(content_lines).strip()
        
        # Ensure we have some content
        if not chunk_text:
            chunk_text = f"Content for {section_title}"
        
        chunk = {
            'doc_name': doc_name,
            'section_title': section_title,
            'page_number': page_num,  # Use 'page_number' instead of 'page_num'
            'content': chunk_text
        }
        chunks.append(chunk)

    return chunks
