#!/usr/bin/env python3
"""
Web Interface for Adobe Hackathon - Round 1A and Round 1B
Flask web application to make the PDF processing accessible via web interface
"""

import os
import sys
import json
import tempfile
import shutil
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_file
from werkzeug.utils import secure_filename
import zipfile

# Add the round implementations to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'round1a', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'round1b', 'src'))

# Import the implementations
from pdf_extractor_generic import extract_document_structure as extract_round1a
try:
    from main import main as round1b_main
    from pdf_extractor import extract_document_structure as extract_round1b_structure
    from chunking import create_semantic_chunks
    from semantic_ranker import SemanticRanker
    ROUND1B_AVAILABLE = True
except ImportError:
    ROUND1B_AVAILABLE = False

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main page with challenge selection."""
    return render_template('index.html', round1b_available=ROUND1B_AVAILABLE)

@app.route('/round1a')
def round1a_page():
    """Round 1A interface page."""
    return render_template('round1a.html')

@app.route('/round1b')
def round1b_page():
    """Round 1B interface page."""
    if not ROUND1B_AVAILABLE:
        return jsonify({'error': 'Round 1B is not available. Please ensure models are downloaded.'}), 500
    return render_template('round1b.html')

@app.route('/api/round1a/process', methods=['POST'])
def process_round1a():
    """Process PDF for Round 1A - Document Structure Extraction."""
    try:
        # Check if file was uploaded
        if 'pdf_file' not in request.files:
            return jsonify({'error': 'No PDF file uploaded'}), 400
        
        file = request.files['pdf_file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Only PDF files are allowed'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        # Process with Round 1A
        start_time = datetime.now()
        result, doc = extract_round1a(filepath)
        if doc:
            doc.close()
        end_time = datetime.now()
        
        processing_time = (end_time - start_time).total_seconds()
        
        # Save output
        output_filename = f"round1a_output_{timestamp}.json"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        # Clean up uploaded file
        os.remove(filepath)
        
        # Return results
        return jsonify({
            'success': True,
            'processing_time': processing_time,
            'title': result.get('title', 'N/A'),
            'headings_count': len(result.get('outline', [])),
            'result': result,
            'output_file': output_filename,
            'constraints_met': {
                'time_limit': processing_time <= 10,
                'format_valid': 'title' in result and 'outline' in result
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@app.route('/api/round1b/process', methods=['POST'])
def process_round1b():
    """Process PDFs for Round 1B - Persona-Driven Document Intelligence."""
    if not ROUND1B_AVAILABLE:
        return jsonify({'error': 'Round 1B is not available. Please ensure models are downloaded.'}), 500
    
    try:
        # Check if files were uploaded
        if 'pdf_files' not in request.files:
            return jsonify({'error': 'No PDF files uploaded'}), 400
        
        files = request.files.getlist('pdf_files')
        if len(files) < 3:
            return jsonify({'error': 'Round 1B requires at least 3 PDF files'}), 400
        
        if len(files) > 10:
            return jsonify({'error': 'Round 1B accepts maximum 10 PDF files'}), 400
        
        # Get persona and job from form
        persona = request.form.get('persona', 'Travel Planner')
        job_to_be_done = request.form.get('job_to_be_done', 'Plan a trip')
        
        # Save uploaded files
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_dir = os.path.join(app.config['UPLOAD_FOLDER'], f'round1b_{timestamp}')
        os.makedirs(temp_dir, exist_ok=True)
        
        uploaded_files = []
        for file in files:
            if file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(temp_dir, filename)
                file.save(filepath)
                uploaded_files.append((filename, filepath))
        
        if len(uploaded_files) < 3:
            shutil.rmtree(temp_dir)
            return jsonify({'error': 'At least 3 valid PDF files are required'}), 400
        
        # Process with Round 1B
        start_time = datetime.now()
        
        # Initialize semantic ranker
        models_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
        ranker = SemanticRanker(model_dir=models_dir)
        
        # Process each PDF and collect chunks
        all_chunks = []
        
        for filename, filepath in uploaded_files:
            # Extract structure
            outline_data, doc = extract_round1b_structure(filepath)
            
            # Create chunks
            outline_json = json.dumps(outline_data, indent=2)
            chunks = create_semantic_chunks(filepath, outline_json)
            
            # Rank chunks for this document
            ranked = ranker.rank_chunks(chunks, persona, job_to_be_done)
            
            # Take best chunk from this document
            if ranked:
                best_chunk = ranked[0]
                best_chunk["document"] = filename
                all_chunks.append(best_chunk)
            
            # Close document
            if doc:
                doc.close()
        
        # Sort all chunks by score and take top 5
        top_chunks = sorted(all_chunks, key=lambda x: x.get("score", 0), reverse=True)[:5]
        
        # Build output
        extracted_sections = []
        subsection_analysis = []
        
        for idx, chunk in enumerate(top_chunks, 1):
            extracted_sections.append({
                "document": chunk["document"],
                "section_title": chunk.get("section_title", ""),
                "importance_rank": idx,
                "page_number": chunk.get("page_number", 1)
            })
            
            subsection_analysis.append({
                "document": chunk["document"],
                "refined_text": chunk.get("content", "")[:1000],  # Limit to 1000 chars
                "page_number": chunk.get("page_number", 1)
            })
        
        result = {
            "metadata": {
                "input_documents": [f[0] for f in uploaded_files],
                "persona": persona,
                "job_to_be_done": job_to_be_done,
                "processing_timestamp": datetime.now().isoformat()
            },
            "extracted_sections": extracted_sections,
            "subsection_analysis": subsection_analysis
        }
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # Save output
        output_filename = f"round1b_output_{timestamp}.json"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        # Clean up uploaded files
        shutil.rmtree(temp_dir)
        
        # Return results
        return jsonify({
            'success': True,
            'processing_time': processing_time,
            'documents_processed': len(uploaded_files),
            'extracted_sections': len(extracted_sections),
            'result': result,
            'output_file': output_filename,
            'constraints_met': {
                'time_limit': processing_time <= 60,
                'format_valid': 'metadata' in result and 'extracted_sections' in result
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@app.route('/api/download/<filename>')
def download_output(filename):
    """Download output file."""
    try:
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if os.path.exists(output_path):
            return send_file(output_path, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

@app.route('/api/status')
def status():
    """Get system status."""
    return jsonify({
        'round1a_available': True,
        'round1b_available': ROUND1B_AVAILABLE,
        'models_loaded': ROUND1B_AVAILABLE,
        'upload_limit_mb': app.config['MAX_CONTENT_LENGTH'] // (1024 * 1024)
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)