#!/usr/bin/env python3

import os
import time
from pathlib import Path
from flask import Flask, request, jsonify, send_file, render_template, redirect
from werkzeug.utils import secure_filename
from md_to_pdf import convert_markdown_to_pdf
from utils.latex_style_pdf_generator import LaTeXStylePDFGenerator

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create necessary directories
UPLOADS_DIR = Path('uploads')
DOWNLOADS_DIR = Path('downloads')
PUBLIC_DIR = Path('public')

for directory in [UPLOADS_DIR, DOWNLOADS_DIR, PUBLIC_DIR]:
    directory.mkdir(exist_ok=True)

@app.route('/')
def index():
    """Serve the main HTML interface."""
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_file():
    """Handle file upload and conversion."""
    try:
        # Check if file was uploaded
        if 'markdown' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['markdown']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        if not file.filename.lower().endswith(('.md', '.markdown')):
            return jsonify({'error': 'Invalid file type. Please upload a Markdown file.'}), 400
        
        # Secure the filename
        filename = secure_filename(file.filename)
        timestamp = str(int(time.time() * 1000))
        safe_filename = f"{timestamp}-{filename}"
        
        # Save uploaded file
        upload_path = UPLOADS_DIR / safe_filename
        file.save(upload_path)
        
        # Convert to PDF
        pdf_filename = Path(safe_filename).stem + '.pdf'
        pdf_path = DOWNLOADS_DIR / pdf_filename
        
        convert_markdown_to_pdf(str(upload_path), str(pdf_path))
        
        # Clean up uploaded file
        upload_path.unlink()
        
        return jsonify({
            'success': True,
            'filename': pdf_filename,
            'message': 'File converted successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Serve converted PDF files for download."""
    try:
        file_path = DOWNLOADS_DIR / filename
        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/convert-resume', methods=['POST'])
def convert_resume():
    """Convert tailored resume to PDF using LaTeX-style formatting."""
    try:
        # Get the resume data from the request
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract resume data
        tailored_resume = data.get('resume_data', {})
        job_title = data.get('job_title', 'Software Engineer')
        company_name = data.get('company_name', 'Company')
        
        if not tailored_resume:
            return jsonify({'error': 'No resume data provided'}), 400
        
        # Generate PDF using LaTeX-style generator
        pdf_generator = LaTeXStylePDFGenerator(str(DOWNLOADS_DIR))
        pdf_path = pdf_generator.generate_pdf(tailored_resume, job_title, company_name)
        
        # Extract filename from path
        pdf_filename = os.path.basename(pdf_path)
        
        return jsonify({
            'success': True,
            'filename': pdf_filename,
            'message': 'Resume converted successfully with LaTeX-style formatting'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Cleanup old files on startup
def cleanup_old_files():
    """Remove files older than 1 hour."""
    current_time = time.time()
    for directory in [UPLOADS_DIR, DOWNLOADS_DIR]:
        for file_path in directory.glob('*'):
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                if file_age > 3600:  # 1 hour
                    try:
                        file_path.unlink()
                        print(f"Cleaned up old file: {file_path}")
                    except Exception as e:
                        print(f"Error cleaning up {file_path}: {e}")

if __name__ == '__main__':
    print("🚀 Starting JobGenie Server...")
    cleanup_old_files()
    print("📁 Directories initialized")
    print("🌐 Server running at http://localhost:3001")
    print("📄 Ready for resume tailoring and PDF conversion!")
    
    app.run(host='0.0.0.0', port=3001, debug=True)