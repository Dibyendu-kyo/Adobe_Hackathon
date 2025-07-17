import sys
sys.path.append('src')
from pdf_extractor import get_document_text_data, extract_pdf_outline
from chunking import create_semantic_chunks
import json

# Get the raw text data
lines_data = get_document_text_data('sample.pdf')

# Show first 20 lines to see what we're getting
print('First 20 lines of extracted text:')
for i, line in enumerate(lines_data[:20]):
    print(f'{i}: Page {line["page_num"]}, Font: {line["font_size"]:.1f}, Text: "{line["text"]}"')

print(f'\nTotal lines extracted: {len(lines_data)}')

# Test chunking
outline_json = extract_pdf_outline('sample.pdf')
chunks = create_semantic_chunks('sample.pdf', outline_json)

print(f'\nFirst 3 chunks:')
for i, chunk in enumerate(chunks[:3]):
    print(f'\nChunk {i+1}:')
    print(f'Section: {chunk["section_title"]}')
    print(f'Content length: {len(chunk["content"])}')
    print(f'Content preview: {chunk["content"][:200]}...')