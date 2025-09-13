#!/usr/bin/env python3

import os
import time
from pathlib import Path
from flask import Flask, request, jsonify, send_file, render_template, redirect
from werkzeug.utils import secure_filename
from md_to_pdf import convert_markdown_to_pdf
# Add imports for URL scraping
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create necessary directories
UPLOADS_DIR = Path('uploads')
DOWNLOADS_DIR = Path('downloads')
PUBLIC_DIR = Path('public')

for directory in [UPLOADS_DIR, DOWNLOADS_DIR, PUBLIC_DIR]:
    directory.mkdir(exist_ok=True)

def scrape_job_description(url):
    """Scrape job description from a URL and return the text content."""
    try:
        # Add a small delay to avoid overwhelming the server
        time.sleep(1)
        
        # Make the request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
        
        # Extract text content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract text from the page (removing script and style elements)
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text(separator='\n', strip=True)
        
        return {
            'success': True,
            'text': text,
            'url': url
        }
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': f"Error downloading {url}: {e}"
        }
    except Exception as e:
        return {
            'success': False,
            'error': f"Unexpected error processing {url}: {e}"
        }

@app.route('/')
def index():
    """Serve the main HTML interface."""
    return render_template('index.html')

@app.route('/scrape-job', methods=['POST'])
def scrape_job():
    """Scrape job description from a URL."""
    try:
        data = request.json
        if not data or 'url' not in data:
            return jsonify({'error': 'No URL provided'}), 400
        
        url = data['url'].strip()
        if not url:
            return jsonify({'error': 'Empty URL provided'}), 400
        
        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        result = scrape_job_description(url)
        
        if result['success']:
            return jsonify({
                'success': True,
                'text': result['text'],
                'url': result['url']
            })
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
    """Convert tailored resume to PDF."""
    try:
        # Get the markdown content from the request
        data = request.json
        if not data or 'markdown' not in data:
            return jsonify({'error': 'No markdown content provided'}), 400
        
        markdown_content = data['markdown']
        
        # Create a temporary markdown file
        timestamp = str(int(time.time() * 1000))
        md_filename = f"{timestamp}-tailored_resume.md"
        md_path = UPLOADS_DIR / md_filename
        
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        # Convert to PDF
        pdf_filename = f"{timestamp}-tailored_resume.pdf"
        pdf_path = DOWNLOADS_DIR / pdf_filename
        
        convert_markdown_to_pdf(str(md_path), str(pdf_path))
        
        # Clean up markdown file
        md_path.unlink()
        
        return jsonify({
            'success': True,
            'filename': pdf_filename,
            'message': 'Resume converted successfully'
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