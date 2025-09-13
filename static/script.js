document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const resumeUpload = document.getElementById('resume-upload');
    const jobUpload = document.getElementById('job-upload');
    const resumePreview = document.getElementById('resume-preview');
    const jobPreview = document.getElementById('job-preview');
    const generateBtn = document.getElementById('generate-btn');
    const resultSection = document.getElementById('result-section');
    const resultContent = document.getElementById('result-content');
    const downloadTxtBtn = document.getElementById('download-txt-btn');
    const downloadPdfBtn = document.getElementById('download-pdf-btn');
    const downloadMdBtn = document.getElementById('download-md-btn');
    
    // Bulk URL scraping elements
    const urlsUpload = document.getElementById('urls-upload');
    const urlsPreview = document.getElementById('urls-preview');
    const scrapeUrlsBtn = document.getElementById('scrape-urls-btn');
    const scrapingResults = document.getElementById('scraping-results');
    const resultsSummary = document.getElementById('results-summary');
    const resultsDetails = document.getElementById('results-details');

    // File contents
    let resumeContent = '';
    let jobContent = '';
    let urlsFileContent = '';

    // Handle file uploads
    if (resumeUpload) {
        resumeUpload.addEventListener('change', (event) => {
            handleFileUpload(event, resumePreview, 'resume');
        });
    }

    if (jobUpload) {
        jobUpload.addEventListener('change', (event) => {
            handleFileUpload(event, jobPreview, 'job');
        });
    }
    
    if (urlsUpload) {
        urlsUpload.addEventListener('change', (event) => {
            handleUrlsFileUpload(event);
        });
    }

    // Generate button click
    generateBtn.addEventListener('click', generateTailoredResume);

    // Download buttons click
    downloadTxtBtn.addEventListener('click', downloadTailoredResumeAsTxt);
    downloadPdfBtn.addEventListener('click', downloadTailoredResumeAsPdf);
    downloadMdBtn.addEventListener('click', downloadTailoredResumeAsMarkdown);
    
    // Bulk scraping button click
    if (scrapeUrlsBtn) {
        scrapeUrlsBtn.addEventListener('click', scrapeBulkUrls);
    }

    /**
     * Handle file upload and preview
     */
    function handleFileUpload(event, previewElement, fileType) {
        const file = event.target.files[0];
        if (!file) {
            return;
        }

        // Show file name in preview immediately
        previewElement.innerHTML = `<p style="color: blue;">Loading file: ${file.name}...</p>`;

        // Check if file is a text file
        if (file.type !== 'text/plain' && !file.name.endsWith('.txt')) {
            previewElement.innerHTML = `<p style="color: red;">Error: Please upload a text (.txt) file</p>`;
            event.target.value = '';
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            const content = e.target.result;
            
            // Show preview with file info
            previewElement.innerHTML = `
                <p style="color: green;">✓ File loaded: ${file.name}</p>
                <p style="font-size: 12px; color: #666;">Size: ${content.length} characters</p>
                <div style="max-height: 200px; overflow-y: auto; border: 1px solid #ccc; padding: 10px; margin-top: 10px; font-family: monospace; font-size: 12px;">
                    ${content.substring(0, 500)}${content.length > 500 ? '...' : ''}
                </div>
            `;
            
            // Store content
            if (fileType === 'resume') {
                resumeContent = content;
            } else if (fileType === 'job') {
                jobContent = content;
            }

            // Enable generate button if both files are uploaded
            if (resumeContent && jobContent && generateBtn) {
                generateBtn.disabled = false;
                generateBtn.style.backgroundColor = '#007bff';
                generateBtn.style.color = 'white';
            }
        };

        reader.onerror = () => {
            previewElement.innerHTML = `<p style="color: red;">Error reading file: ${file.name}</p>`;
        };

        reader.readAsText(file);
    }

    /**
     * Generate tailored resume based on uploaded files
     */
    function generateTailoredResume() {
        if (!resumeContent || !jobContent) {
            alert('Please upload both resume and job description files');
            return;
        }

        // Show loading state
        resultContent.innerHTML = '<p class="placeholder-text">Processing... Please wait.</p>';
        generateBtn.disabled = true;

        // In a real application, this would call an API with GPT-4
        // For this demo, we'll simulate processing with a timeout
        setTimeout(() => {
            // Simple processing logic (in a real app, this would use GPT-4)
            const processedResume = processResume(resumeContent, jobContent);
            
            // Display result
            resultContent.textContent = processedResume;
            downloadTxtBtn.disabled = false;
            downloadPdfBtn.disabled = false;
            downloadMdBtn.disabled = false;
            generateBtn.disabled = false;
        }, 2000);
    }

    /**
     * Simple resume processing logic (placeholder for GPT-4 integration)
     */
    function processResume(resume, jobDescription) {
        // This is a simplified version of what would normally be done with GPT-4
        // In a real application, this would send the data to a backend API
        
        // Extract keywords from job description (simplified)
        const jobKeywords = extractKeywords(jobDescription);
        
        // Split resume into sections
        const sections = resume.split('\n\n');
        
        // Filter sections that contain job keywords (simplified matching)
        let relevantSections = sections.filter(section => {
            return jobKeywords.some(keyword => 
                section.toLowerCase().includes(keyword.toLowerCase()));
        });
        
        // Limit the number of sections to ensure resume fits in 1-2 pages
        // Prioritize sections with more keyword matches
        relevantSections = prioritizeSections(relevantSections, jobKeywords);
        
        // Start with an empty header
        const header = "";
        
        // Combine relevant sections
        return header + relevantSections.join('\n\n');
    }

    /**
     * Prioritize sections based on keyword matches to limit resume length
     */
    function prioritizeSections(sections, keywords) {
        // Score each section based on keyword matches
        const scoredSections = sections.map(section => {
            let score = 0;
            keywords.forEach(keyword => {
                // Count occurrences of each keyword
                const regex = new RegExp(keyword, 'gi');
                const matches = section.match(regex);
                if (matches) {
                    score += matches.length;
                }
            });
            return { section, score };
        });
        
        // Sort sections by score (highest first)
        scoredSections.sort((a, b) => b.score - a.score);
        
        // Take only top sections to fit in 1-2 pages (approximately 1500 characters)
        let totalLength = 0;
        const maxLength = 1500; // Target character count for 1-2 pages
        const selectedSections = [];
        
        for (const { section } of scoredSections) {
            if (totalLength + section.length <= maxLength) {
                selectedSections.push(section);
                totalLength += section.length + 2; // +2 for the newline characters
            } else if (selectedSections.length === 0) {
                // If we haven't added any sections yet, add at least one
                selectedSections.push(section);
                break;
            } else {
                break;
            }
        }
        
        return selectedSections;
    }

    /**
     * Extract keywords from job description (simplified)
     */
    function extractKeywords(jobDescription) {
        // In a real application, this would use NLP or GPT-4
        // For this demo, we'll use a simple approach
        
        // Remove common words and punctuation
        const text = jobDescription.toLowerCase()
            .replace(/[.,\/#!$%\^&\*;:{}=\-_`~()]/g, '')
            .replace(/\s{2,}/g, ' ');
        
        // Split into words
        const words = text.split(' ');
        
        // Filter common words (very simplified)
        const commonWords = ['and', 'the', 'to', 'of', 'a', 'in', 'for', 'is', 'on', 'that', 'by', 'this', 'with', 'i', 'you', 'it', 'not', 'or', 'be', 'are', 'from', 'at', 'as', 'your', 'have', 'more', 'an', 'was'];
        const filteredWords = words.filter(word => 
            word.length > 3 && !commonWords.includes(word));
        
        // Count word frequency
        const wordCount = {};
        filteredWords.forEach(word => {
            wordCount[word] = (wordCount[word] || 0) + 1;
        });
        
        // Sort by frequency and take top 15
        const sortedWords = Object.entries(wordCount)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 15)
            .map(entry => entry[0]);
        
        return sortedWords;
    }

    /**
     * Download tailored resume as text file
     */
    function downloadTailoredResumeAsTxt() {
        const content = resultContent.textContent;
        if (!content || content.includes('Your tailored resume will appear here')) {
            alert('No resume to download');
            return;
        }

        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'tailored_resume.txt';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    /**
     * Download tailored resume as PDF file using server-side conversion
     */
    function downloadTailoredResumeAsPdf() {
        const content = resultContent.textContent;
        if (!content || content.includes('Your tailored resume will appear here')) {
            alert('No resume to download');
            return;
        }

        // First convert to markdown
        const markdownContent = convertToMarkdown(content);
        
        // Show loading indicator
        const originalText = resultContent.innerHTML;
        resultContent.innerHTML = '<p class="placeholder-text">Generating PDF... Please wait.</p>';
        
        // Send to server for conversion
        fetch('/convert-resume', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ markdown: markdownContent })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Automatically trigger download
                const downloadUrl = `/download/${data.filename}`;
                const link = document.createElement('a');
                link.href = downloadUrl;
                link.download = data.filename;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                
                // Restore original content
                resultContent.innerHTML = originalText;
            } else {
                alert(`Error: ${data.error}`);
                resultContent.innerHTML = originalText;
            }
        })
        .catch(error => {
            alert(`Network error: ${error.message}`);
            resultContent.innerHTML = originalText;
        });
    }

    /**
     * Download tailored resume as Markdown file
     */
    function downloadTailoredResumeAsMarkdown() {
        const content = resultContent.textContent;
        if (!content || content.includes('Your tailored resume will appear here')) {
            alert('No resume to download');
            return;
        }

        // Convert plain text to markdown format
        const markdownContent = convertToMarkdown(content);
        
        // Create and download the markdown file
        const blob = new Blob([markdownContent], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'tailored_resume.md';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    /**
     * Convert plain text resume to markdown format
     */
    function convertToMarkdown(text) {
        // Split the text into sections
        const sections = text.split('\n\n');
        let markdownContent = '';
        
        // Process each section
        for (let i = 0; i < sections.length; i++) {
            const section = sections[i].trim();
            
            // Skip empty sections
            if (!section) continue;
            
            // Check if this is a header (all caps)
            const isHeader = section.toUpperCase() === section && section.length > 0;
            
            if (isHeader) {
                // Format as markdown header
                if (i === 0) {
                    // First header is the title - use H1
                    markdownContent += `# ${section}\n\n`;
                } else {
                    // Other headers use H2
                    markdownContent += `## ${section}\n\n`;
                }
            } else if (section.startsWith('- ')) {
                // Already a list, keep as is
                markdownContent += `${section}\n\n`;
            } else if (section.includes(':\n')) {
                // Section with a title and content
                const [title, ...content] = section.split(':\n');
                markdownContent += `### ${title.trim()}\n\n${content.join(':\n')}\n\n`;
            } else {
                // Regular paragraph
                markdownContent += `${section}\n\n`;
            }
        }
        
        return markdownContent;
    }

    /**
     * Handle URLs file upload
     */
    function handleUrlsFileUpload(event) {
        const file = event.target.files[0];
        if (!file) {
            return;
        }

        // Show file name in preview immediately
        urlsPreview.innerHTML = `<p style="color: blue;">Loading file: ${file.name}...</p>`;

        // Check if file is a text or CSV file
        if (!file.name.toLowerCase().endsWith('.txt') && !file.name.toLowerCase().endsWith('.csv')) {
            urlsPreview.innerHTML = `<p style="color: red;">Error: Please upload a .txt or .csv file</p>`;
            event.target.value = '';
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            const content = e.target.result;
            
            // Parse URLs from content
            const urls = content.split('\n')
                .map(line => line.trim())
                .filter(line => line.length > 0);
            
            if (urls.length === 0) {
                urlsPreview.innerHTML = `<p style="color: red;">Error: No valid URLs found in file</p>`;
                event.target.value = '';
                return;
            }
            
            // Show preview with file info
            urlsPreview.innerHTML = `
                <p style="color: green;">✓ File loaded: ${file.name}</p>
                <p style="font-size: 12px; color: #666;">Found ${urls.length} URLs</p>
                <div style="max-height: 200px; overflow-y: auto; border: 1px solid #ccc; padding: 10px; margin-top: 10px; font-family: monospace; font-size: 12px;">
                    ${urls.slice(0, 10).join('\n')}${urls.length > 10 ? '\n... and ' + (urls.length - 10) + ' more' : ''}
                </div>
            `;
            
            // Store content and enable scrape button
            urlsFileContent = content;
            scrapeUrlsBtn.disabled = false;
            scrapeUrlsBtn.style.backgroundColor = '#28a745';
            scrapeUrlsBtn.style.color = 'white';
        };

        reader.onerror = () => {
            urlsPreview.innerHTML = `<p style="color: red;">Error reading file: ${file.name}</p>`;
        };

        reader.readAsText(file);
    }

    /**
     * Scrape URLs from uploaded file
     */
    function scrapeBulkUrls() {
        if (!urlsFileContent) {
            alert('Please upload a URLs file first');
            return;
        }

        // Show loading state
        scrapeUrlsBtn.disabled = true;
        scrapeUrlsBtn.textContent = 'Scraping URLs...';
        scrapingResults.style.display = 'block';
        resultsSummary.innerHTML = '<p style="color: blue;">Processing URLs... Please wait.</p>';
        resultsDetails.innerHTML = '';

        // Create FormData for file upload
        const formData = new FormData();
        const blob = new Blob([urlsFileContent], { type: 'text/plain' });
        formData.append('urls_file', blob, 'urls.txt');

        // Send request to scrape-urls-file endpoint
        fetch('/scrape-urls-file', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayScrapingResults(data);
            } else {
                resultsSummary.innerHTML = `<p style="color: red;">Error: ${data.error}</p>`;
            }
        })
        .catch(error => {
            resultsSummary.innerHTML = `<p style="color: red;">Network error: ${error.message}</p>`;
        })
        .finally(() => {
            // Reset button state
            scrapeUrlsBtn.disabled = false;
            scrapeUrlsBtn.textContent = 'Scrape Job URLs';
        });
    }

    /**
     * Display scraping results
     */
    function displayScrapingResults(data) {
        const { summary, results, message } = data;
        
        // Display summary
        resultsSummary.innerHTML = `
            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 15px;">
                <h4 style="margin: 0 0 10px 0; color: #28a745;">✓ Scraping Complete</h4>
                <p style="margin: 5px 0;"><strong>Total URLs:</strong> ${summary.total}</p>
                <p style="margin: 5px 0; color: #28a745;"><strong>Successful:</strong> ${summary.success}</p>
                <p style="margin: 5px 0; color: #dc3545;"><strong>Failed:</strong> ${summary.failed}</p>
                <p style="margin: 5px 0; font-size: 12px; color: #666;">${message}</p>
            </div>
        `;
        
        // Display detailed results
        let detailsHtml = '<div style="max-height: 400px; overflow-y: auto;">';
        
        results.forEach((result, index) => {
            const statusColor = result.success ? '#28a745' : '#dc3545';
            const statusIcon = result.success ? '✓' : '✗';
            
            detailsHtml += `
                <div style="border: 1px solid #dee2e6; margin-bottom: 10px; padding: 10px; border-radius: 5px;">
                    <div style="display: flex; align-items: center; margin-bottom: 5px;">
                        <span style="color: ${statusColor}; font-weight: bold; margin-right: 10px;">${statusIcon}</span>
                        <span style="font-size: 12px; color: #666; word-break: break-all;">${result.url}</span>
                    </div>
            `;
            
            if (result.success) {
                const textPreview = result.text.substring(0, 200) + (result.text.length > 200 ? '...' : '');
                detailsHtml += `
                    <p style="margin: 5px 0; font-size: 12px; color: #28a745;">Saved as: ${result.filename}</p>
                    <div style="background: #f8f9fa; padding: 8px; font-size: 11px; color: #666; border-radius: 3px;">
                        ${textPreview.replace(/\n/g, '<br>')}
                    </div>
                `;
            } else {
                detailsHtml += `
                    <p style="margin: 5px 0; font-size: 12px; color: #dc3545;">Error: ${result.error}</p>
                `;
            }
            
            detailsHtml += '</div>';
        });
        
        detailsHtml += '</div>';
        resultsDetails.innerHTML = detailsHtml;
    }
});