#!/usr/bin/env python3

import os
import time
from pathlib import Path
from flask import Flask, request, jsonify, send_file, render_template_string
from werkzeug.utils import secure_filename
from md_to_pdf import convert_markdown_to_pdf

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create necessary directories
UPLOADS_DIR = Path('uploads')
DOWNLOADS_DIR = Path('downloads')
PUBLIC_DIR = Path('public')

for directory in [UPLOADS_DIR, DOWNLOADS_DIR, PUBLIC_DIR]:
    directory.mkdir(exist_ok=True)

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Markdown to PDF Converter</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }

        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            font-weight: 700;
        }

        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }

        .main-content {
            padding: 40px;
        }

        .upload-area {
            border: 3px dashed #e2e8f0;
            border-radius: 15px;
            padding: 60px 40px;
            text-align: center;
            transition: all 0.3s ease;
            cursor: pointer;
            background: #f8fafc;
        }

        .upload-area:hover {
            border-color: #4facfe;
            background: #f0f9ff;
        }

        .upload-area.dragover {
            border-color: #4facfe;
            background: #e0f2fe;
            transform: scale(1.02);
        }

        .upload-icon {
            font-size: 4rem;
            color: #94a3b8;
            margin-bottom: 20px;
        }

        .upload-text {
            font-size: 1.2rem;
            color: #475569;
            margin-bottom: 10px;
        }

        .upload-subtext {
            color: #94a3b8;
            font-size: 0.9rem;
        }

        #fileInput {
            display: none;
        }

        .file-info {
            display: none;
            background: #f1f5f9;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
        }

        .file-name {
            font-weight: 600;
            color: #334155;
            margin-bottom: 5px;
        }

        .file-size {
            color: #64748b;
            font-size: 0.9rem;
        }

        .convert-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            border-radius: 50px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 20px;
            width: 100%;
        }

        .convert-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }

        .convert-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .progress-bar {
            display: none;
            width: 100%;
            height: 8px;
            background: #e2e8f0;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 20px;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
            width: 0%;
            transition: width 0.3s ease;
        }

        .result {
            display: none;
            margin-top: 20px;
            padding: 20px;
            border-radius: 10px;
        }

        .result.success {
            background: #dcfce7;
            border: 1px solid #bbf7d0;
            color: #166534;
        }

        .result.error {
            background: #fef2f2;
            border: 1px solid #fecaca;
            color: #dc2626;
        }

        .download-btn {
            background: #10b981;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            text-decoration: none;
            display: inline-block;
            margin-top: 10px;
            font-weight: 500;
            transition: background 0.3s ease;
        }

        .download-btn:hover {
            background: #059669;
        }

        .features {
            margin-top: 40px;
            padding-top: 40px;
            border-top: 1px solid #e2e8f0;
        }

        .features h3 {
            text-align: center;
            margin-bottom: 30px;
            color: #334155;
            font-size: 1.5rem;
        }

        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }

        .feature {
            text-align: center;
            padding: 20px;
        }

        .feature-icon {
            font-size: 2.5rem;
            margin-bottom: 15px;
        }

        .feature h4 {
            margin-bottom: 10px;
            color: #334155;
        }

        .feature p {
            color: #64748b;
            line-height: 1.6;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📄 Markdown to PDF</h1>
            <p>Convert your Markdown files to professional PDFs instantly</p>
        </div>
        
        <div class="main-content">
            <div class="upload-area" onclick="document.getElementById('fileInput').click()">
                <div class="upload-icon">📁</div>
                <div class="upload-text">Click to select or drag & drop your Markdown file</div>
                <div class="upload-subtext">Supports .md and .markdown files (max 16MB)</div>
            </div>
            
            <input type="file" id="fileInput" accept=".md,.markdown" />
            
            <div class="file-info" id="fileInfo">
                <div class="file-name" id="fileName"></div>
                <div class="file-size" id="fileSize"></div>
            </div>
            
            <button class="convert-btn" id="convertBtn" onclick="convertFile()" disabled>
                Convert to PDF
            </button>
            
            <div class="progress-bar" id="progressBar">
                <div class="progress-fill" id="progressFill"></div>
            </div>
            
            <div class="result" id="result"></div>
            
            <div class="features">
                <h3>✨ Features</h3>
                <div class="features-grid">
                    <div class="feature">
                        <div class="feature-icon">🎨</div>
                        <h4>Professional Styling</h4>
                        <p>Clean, modern design optimized for resumes and documents</p>
                    </div>
                    <div class="feature">
                        <div class="feature-icon">⚡</div>
                        <h4>Fast Conversion</h4>
                        <p>Lightning-fast processing with high-quality output</p>
                    </div>
                    <div class="feature">
                        <div class="feature-icon">🔒</div>
                        <h4>Secure & Private</h4>
                        <p>Files are processed locally and automatically cleaned up</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let selectedFile = null;

        // File input change handler
        document.getElementById('fileInput').addEventListener('change', function(e) {
            handleFileSelect(e.target.files[0]);
        });

        // Drag and drop handlers
        const uploadArea = document.querySelector('.upload-area');
        
        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', function(e) {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFileSelect(files[0]);
            }
        });

        function handleFileSelect(file) {
            if (!file) return;
            
            // Validate file type
            const validTypes = ['.md', '.markdown'];
            const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
            
            if (!validTypes.includes(fileExtension)) {
                showResult('Please select a valid Markdown file (.md or .markdown)', 'error');
                return;
            }
            
            selectedFile = file;
            
            // Show file info
            document.getElementById('fileName').textContent = file.name;
            document.getElementById('fileSize').textContent = formatFileSize(file.size);
            document.getElementById('fileInfo').style.display = 'block';
            document.getElementById('convertBtn').disabled = false;
            
            // Hide previous results
            document.getElementById('result').style.display = 'none';
        }

        function formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }

        async function convertFile() {
            if (!selectedFile) return;
            
            const convertBtn = document.getElementById('convertBtn');
            const progressBar = document.getElementById('progressBar');
            const progressFill = document.getElementById('progressFill');
            
            // Show progress and disable button
            convertBtn.disabled = true;
            convertBtn.textContent = 'Converting...';
            progressBar.style.display = 'block';
            progressFill.style.width = '0%';
            
            // Animate progress
            let progress = 0;
            const progressInterval = setInterval(() => {
                progress += Math.random() * 15;
                if (progress > 90) progress = 90;
                progressFill.style.width = progress + '%';
            }, 100);
            
            try {
                const formData = new FormData();
                formData.append('markdown', selectedFile);
                
                const response = await fetch('/convert', {
                    method: 'POST',
                    body: formData
                });
                
                clearInterval(progressInterval);
                progressFill.style.width = '100%';
                
                if (response.ok) {
                    const result = await response.json();
                    
                    // Automatically trigger download
                    const downloadUrl = `/download/${result.filename}`;
                    const link = document.createElement('a');
                    link.href = downloadUrl;
                    link.download = result.filename;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    
                    showResult(
                        `✅ Conversion successful! Your PDF has been downloaded automatically.`,
                        'success'
                    );
                } else {
                    const error = await response.json();
                    showResult(`❌ Error: ${error.error}`, 'error');
                }
            } catch (error) {
                clearInterval(progressInterval);
                showResult(`❌ Network error: ${error.message}`, 'error');
            } finally {
                // Reset UI
                setTimeout(() => {
                    convertBtn.disabled = false;
                    convertBtn.textContent = 'Convert to PDF';
                    progressBar.style.display = 'none';
                }, 1000);
            }
        }

        function showResult(message, type) {
            const result = document.getElementById('result');
            result.innerHTML = message;
            result.className = `result ${type}`;
            result.style.display = 'block';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Serve the main HTML interface."""
    return render_template_string(HTML_TEMPLATE)

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
    print("🚀 Starting Markdown to PDF Converter Server...")
    cleanup_old_files()
    print("📁 Directories initialized")
    print("🌐 Server running at http://localhost:3001")
    print("📄 Ready for markdown file uploads!")
    
    app.run(host='0.0.0.0', port=3001, debug=True)