import fitz  # PyMuPDF
import json
import re
import os
import torch
from sentence_transformers import SentenceTransformer, CrossEncoder, util
from collections import Counter, defaultdict

# --- Part 1: Document Structure Extractor (Round 1A) ---
def extract_document_structure(pdf_path):
    """
    Extracts a structured outline using a robust, non-hardcoded approach, compliant with Adobe's constraints.
    """
    doc = fitz.open(pdf_path)
    output = {"title": "Title Not Found", "outline": []}
    headings = []
    font_counts = Counter()
    font_size_to_lines = defaultdict(list)
    page_texts = []
    page_headings = defaultdict(list)

    # 1. Profile the document's body text to establish a baseline.
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

    body_text_style = font_counts.most_common(1)[0][0]
    body_text_size = body_text_style[0]

    # 2. Extract potential headings using multi-factor heuristics.
    for page_num, page in enumerate(doc):
        text_dict = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
        mediabox = page.rect
        for block in text_dict.get("blocks", []):
            if block['type'] == 0:
                if len(block.get("lines", [])) == 1:
                    line = block["lines"][0]
                    line_text = "".join(s['text'] for s in line['spans']).strip()
                    if not line_text:
                        continue
                    span = line['spans'][0]
                    font_size = span['size']
                    font_name = span['font']
                    bbox = span['bbox'] if 'bbox' in span else None
                    is_larger = font_size > body_text_size + 0.5
                    is_bold = "bold" in font_name.lower() or "black" in font_name.lower() or (span['flags'] & 16)
                    is_short = len(line_text.split()) < 25
                    is_not_sentence = not line_text.endswith('.')
                    is_not_date = not re.match(r'^\w+\s\d{1,2},\s\d{4}$', line_text)
                    is_numbered = bool(re.match(r'^(\d+\.|[IVXLC]+\.|[A-Z]\.)', line_text.strip()))
                    is_all_caps = line_text.isupper() and len(line_text) > 3
                    # Centered: check if bbox is roughly centered
                    is_centered = False
                    if bbox:
                        left, top, right, bottom = bbox
                        center_x = (left + right) / 2
                        page_center_x = (mediabox.x0 + mediabox.x1) / 2
                        is_centered = abs(center_x - page_center_x) < (mediabox.width / 8)
                    # Accept heading if any strong signal
                    if (is_larger or is_bold or is_numbered or is_all_caps or is_centered) and is_short and is_not_sentence and is_not_date:
                        headings.append({
                            'text': line_text,
                            'size': font_size,
                            'page': page_num + 1
                        })
                        page_headings[page_num + 1].append(line_text)

    # 3. Try to detect if the first page is a cover (no headings, or very little text)
    # If so, adjust page numbers for headings if needed (but do not hardcode)
    if len(page_headings.get(1, [])) == 0 and len(page_texts) > 1:
        # If first page has no headings and little text, treat as cover
        if len(page_texts[0].strip()) < 200:
            for h in headings:
                h['page'] = max(1, h['page'] - 1)

    # 4. Identify the title: Try PDF metadata, then largest heading on first 2 pages.
    title = None
    try:
        meta = doc.metadata
        if meta and meta.get('title') and meta['title'].strip().lower() != 'untitled':
            title = meta['title'].strip()
    except Exception:
        pass
    if not title:
        first_page_headings = sorted([h for h in headings if h['page'] <= 2], key=lambda x: x['size'], reverse=True)
        if first_page_headings:
            title = first_page_headings[0]['text']
    if not title and headings:
        title = headings[0]['text']
    output['title'] = title if title else "Title Not Found"

    # 5. Cluster headings by font size to assign hierarchy (H1, H2, H3 only)
    if headings:
        unique_sizes = sorted(list(set([h['size'] for h in headings])), reverse=True)
        # Map largest to H1, next to H2, all others to H3
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
        # Assign levels and filter to H1, H2, H3 only
        for h in sorted(headings, key=lambda x: (x['page'], -x['size'])):
            level = size_map.get(h['size'], "H3")
            if level in {"H1", "H2", "H3"}:
                output['outline'].append({
                    "level": level,
                    "text": h['text'],
                    "page": h['page']
                })

    return output, doc

# --- Part 2: Persona-Driven Intelligence Engine (Round 1B) ---
def perform_semantic_analysis(docs_data, persona, job, models):
    """
    Performs semantic analysis with corrected semantic chunking logic.
    """
    embedder, reranker = models
    query = f"Persona: {persona}. Job: {job}"
    
    # [cite_start]1. Correctly create semantic chunks from all documents. [cite: 170]
    all_chunks = []
    for pdf_name, (outline, doc) in docs_data.items():
        full_text = "".join([page.get_text() for page in doc])
        doc_headings = sorted(outline['outline'], key=lambda x: x['page'])
        
        for i, heading in enumerate(doc_headings):
            start_pos = full_text.find(heading['text'])
            if start_pos == -1:
                continue
            
            end_pos = -1
            if i + 1 < len(doc_headings):
                next_heading_text = doc_headings[i+1]['text']
                end_pos = full_text.find(next_heading_text, start_pos)
            
            chunk_content = full_text[start_pos:end_pos].strip()
            if len(chunk_content) > 50:  # Ensure chunk is substantial
                all_chunks.append({
                    'doc': pdf_name,
                    'page': heading['page'],
                    'title': heading['text'],
                    'content': chunk_content
                })
    
    if not all_chunks:
        return {"error": "No content chunks could be created."}
    
    # [cite_start]2. Initial Retrieval with Embedding Model. [cite: 232-238]
    chunk_contents = [chunk['content'] for chunk in all_chunks]
    query_embedding = embedder.encode(query, convert_to_tensor=True)
    chunk_embeddings = embedder.encode(chunk_contents, convert_to_tensor=True)
    cosine_scores = util.cos_sim(query_embedding, chunk_embeddings)[0]
    
    top_k = min(50, len(all_chunks))
    top_results_indices = torch.topk(cosine_scores, k=top_k).indices
    candidate_chunks = [all_chunks[i] for i in top_results_indices]
    
    # [cite_start]3. Final Ranking with Cross-Encoder. [cite: 245-251]
    reranker_pairs = [[query, chunk['content']] for chunk in candidate_chunks]
    reranker_scores = reranker.predict(reranker_pairs)
    
    for i in range(len(candidate_chunks)):
        candidate_chunks[i]['score'] = reranker_scores[i]
    
    ranked_chunks = sorted(candidate_chunks, key=lambda x: x['score'], reverse=True)
    
    # [cite_start]4. Format the final JSON output. [cite: 257]
    final_output = {
        "metadata": {"persona": persona, "job": job},
        "extracted_section": [],
    }
    
    for i, chunk in enumerate(ranked_chunks[:10]):
        final_output["extracted_section"].append({
            "document": chunk['doc'],
            "page_number": chunk['page'],
            "section_title": chunk['title'],
            "section_content_preview": ' '.join(chunk['content'].split()[:50]) + '...',
            "importance_rank": i + 1,
            "relevance_score": float(chunk['score'])
        })
    
    return final_output

# --- Main Execution Logic ---
if __name__ == "__main__":
    INPUT_DIR, OUTPUT_DIR, MODEL_DIR = "./input", "./output", "./models"
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    if not os.path.exists(os.path.join(MODEL_DIR, 'all-MiniLM-L6-v2')):
        print("Models not found. Please run a script to download them first.")
    elif not os.listdir(INPUT_DIR):
        print("Input directory is empty. Please place PDF files in the 'input' folder.")
    else:
        print("Loading models...")
        embedder = SentenceTransformer(os.path.join(MODEL_DIR, 'all-MiniLM-L6-v2'))
        reranker = CrossEncoder(os.path.join(MODEL_DIR, 'cross-encoder-ms-marco-MiniLM-L6-v2'))
        print("Models loaded.")
        
        docs_data = {}
        for filename in os.listdir(INPUT_DIR):
            if filename.lower().endswith('.pdf'):
                pdf_path = os.path.join(INPUT_DIR, filename)
                print(f"Processing for structure: {filename}")
                structure, doc_object = extract_document_structure(pdf_path)
                if doc_object:
                    docs_data[filename] = (structure, doc_object)
        
        persona = "Investment Analyst"
        job = "Analyze revenue trends, R&D investments, and market positioning strategies"
        
        print("\nPerforming semantic analysis...")
        analysis_results = perform_semantic_analysis(docs_data, persona, job, (embedder, reranker))
        
        output_path = os.path.join(OUTPUT_DIR, "analysis_output.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=4, ensure_ascii=False)
        
        print(f"\n✅ Analysis complete. Results saved to {output_path}")