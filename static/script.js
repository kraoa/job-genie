document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const resumeUpload = document.getElementById('resume-upload');
    const jobUpload = document.getElementById('job-upload');
    const resumePreview = document.getElementById('resume-preview');
    const jobPreview = document.getElementById('job-preview');
    const generateBtn = document.getElementById('generate-btn');
    const resultContent = document.getElementById('result-content');
    const downloadTxtBtn = document.getElementById('download-txt-btn');
    const downloadPdfBtn = document.getElementById('download-pdf-btn');
    const downloadMdBtn = document.getElementById('download-md-btn');

    // File contents
    let resumeContent = '';
    let jobContent = '';

    // Handle file uploads
    resumeUpload.addEventListener('change', (event) => {
        handleFileUpload(event, resumePreview, 'resume');
    });

    jobUpload.addEventListener('change', (event) => {
        handleFileUpload(event, jobPreview, 'job');
    });

    // Generate button click
    generateBtn.addEventListener('click', generateTailoredResume);

    // Download buttons click
    downloadTxtBtn.addEventListener('click', downloadTailoredResumeAsTxt);
    downloadPdfBtn.addEventListener('click', downloadTailoredResumeAsPdf);
    downloadMdBtn.addEventListener('click', downloadTailoredResumeAsMarkdown);

    /**
     * Handle file upload and preview
     */
    function handleFileUpload(event, previewElement, fileType) {
        const file = event.target.files[0];
        if (!file) return;

        // Check if file is a text file
        if (file.type !== 'text/plain' && !file.name.endsWith('.txt')) {
            alert('Please upload a text (.txt) file');
            event.target.value = '';
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            const content = e.target.result;
            previewElement.textContent = content;
            
            // Store content
            if (fileType === 'resume') {
                resumeContent = content;
            } else if (fileType === 'job') {
                jobContent = content;
            }

            // Enable generate button if both files are uploaded
            if (resumeContent && jobContent) {
                generateBtn.disabled = false;
            }
        };

        reader.onerror = () => {
            alert('Error reading file');
            previewElement.textContent = '';
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
        
        // Add a header explaining this is a demo
        const header = "DEMO TAILORED RESUME\n" +
                      "(This is a simplified demo without actual GPT-4 integration)\n\n" +
                      "In a real implementation, this would use GPT-4 to intelligently:\n" +
                      "- Extract relevant experience based on job requirements\n" +
                      "- Highlight matching skills and qualifications\n" +
                      "- Reword achievements to match job description language\n" +
                      "- Format the resume professionally\n\n" +
                      "SIMPLIFIED RESULT BASED ON KEYWORD MATCHING:\n\n";
        
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
     * Parse resume content into structured data for PDF generation
     */
    function parseResumeContent(content) {
        const lines = content.split('\n').map(line => line.trim()).filter(line => line);
        
        const resumeData = {
            name: '',
            email: '',
            phone: '',
            location: '',
            linkedin: '',
            github: '',
            summary: '',
            skills: [],
            experience: [],
            education: [],
            projects: [],
            awards: []
        };
        
        let currentSection = '';
        let currentJob = null;
        let currentEdu = null;
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            const lowerLine = line.toLowerCase();
            
            // Skip demo headers
            if (lowerLine.includes('demo tailored resume') || 
                lowerLine.includes('simplified result') ||
                lowerLine.includes('in a real implementation')) {
                continue;
            }
            
            // Extract contact information from first few lines
            if (i < 3 && !resumeData.name) {
                if (line.includes('@')) {
                    resumeData.email = line;
                } else if (line.includes('(') && line.includes(')')) {
                    resumeData.phone = line;
                } else if (line.includes('linkedin.com')) {
                    resumeData.linkedin = line;
                } else if (line.includes('github.com')) {
                    resumeData.github = line;
                } else if (!resumeData.name && !line.includes('|') && !line.includes('@')) {
                    resumeData.name = line;
                }
            }
            
            // Detect sections
            if (lowerLine.includes('summary') || lowerLine.includes('profile') || lowerLine.includes('objective')) {
                currentSection = 'summary';
            } else if (lowerLine.includes('skills') || lowerLine.includes('technical skills')) {
                currentSection = 'skills';
            } else if (lowerLine.includes('experience') || lowerLine.includes('work experience')) {
                currentSection = 'experience';
            } else if (lowerLine.includes('education') || lowerLine.includes('academic')) {
                currentSection = 'education';
            } else if (lowerLine.includes('projects') || lowerLine.includes('project experience')) {
                currentSection = 'projects';
            } else if (lowerLine.includes('awards') || lowerLine.includes('achievements')) {
                currentSection = 'awards';
            } else {
                // Process content based on current section
                if (currentSection === 'summary' && line && !line.includes('SUMMARY')) {
                    resumeData.summary += line + ' ';
                } else if (currentSection === 'skills' && line && !line.includes('SKILLS')) {
                    if (line.startsWith('-')) {
                        resumeData.skills.push(line.substring(1).trim());
                    } else {
                        resumeData.skills.push(line);
                    }
                } else if (currentSection === 'experience' && line && !line.includes('EXPERIENCE')) {
                    // Check if this is a job title (usually in caps or title case)
                    if (line === line.toUpperCase() && line.length > 5 && !line.includes('|') && !line.includes('-')) {
                        if (currentJob) {
                            resumeData.experience.push(currentJob);
                        }
                        currentJob = { title: line, company: '', duration: '', location: '', description: [] };
                    } else if (currentJob && line.includes('|')) {
                        // Company and location line
                        const parts = line.split('|');
                        currentJob.company = parts[0].trim();
                        if (parts.length > 1) {
                            currentJob.location = parts[1].trim();
                        }
                        if (parts.length > 2) {
                            currentJob.duration = parts[2].trim();
                        }
                    } else if (currentJob && line.startsWith('-')) {
                        // Job description bullet point
                        currentJob.description.push(line.substring(1).trim());
                    }
                } else if (currentSection === 'education' && line && !line.includes('EDUCATION')) {
                    if (line === line.toUpperCase() && line.length > 5 && !line.includes('|')) {
                        if (currentEdu) {
                            resumeData.education.push(currentEdu);
                        }
                        currentEdu = { degree: line, institution: '', year: '', location: '' };
                    } else if (currentEdu && line.includes('|')) {
                        const parts = line.split('|');
                        currentEdu.institution = parts[0].trim();
                        if (parts.length > 1) {
                            currentEdu.location = parts[1].trim();
                        }
                        if (parts.length > 2) {
                            currentEdu.year = parts[2].trim();
                        }
                    }
                } else if (currentSection === 'projects' && line && !line.includes('PROJECTS')) {
                    if (line.startsWith('-')) {
                        resumeData.projects.push(line.substring(1).trim());
                    } else {
                        resumeData.projects.push(line);
                    }
                } else if (currentSection === 'awards' && line && !line.includes('AWARDS')) {
                    if (line.startsWith('-')) {
                        resumeData.awards.push(line.substring(1).trim());
                    } else {
                        resumeData.awards.push(line);
                    }
                }
            }
        }
        
        // Add the last job and education entries
        if (currentJob) {
            resumeData.experience.push(currentJob);
        }
        if (currentEdu) {
            resumeData.education.push(currentEdu);
        }
        
        // Clean up summary
        resumeData.summary = resumeData.summary.trim();
        
        return resumeData;
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

        // Parse the resume content into structured data
        const resumeData = parseResumeContent(content);
        
        // Get job title and company from the form
        const jobTitle = document.getElementById('job-title').value || 'Software Engineer';
        const companyName = document.getElementById('company-name').value || 'Company';
        
        // Show loading indicator
        const originalText = resultContent.innerHTML;
        resultContent.innerHTML = '<p class="placeholder-text">Generating PDF... Please wait.</p>';
        
        // Send to server for conversion
        fetch('/convert-resume', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                resume_data: resumeData,
                job_title: jobTitle,
                company_name: companyName
            })
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
});