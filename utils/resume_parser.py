#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Resume Parser Module

This module extracts structured information from a resume in PDF, DOCX, or Markdown format.
It categorizes content into sections like education, skills, experience, etc.
"""

import re
import os
import pdfplumber
import docx
import spacy
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

# Ensure NLTK data is downloaded
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')

# Load spaCy model
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    print("Downloading spaCy model...")
    os.system('python -m spacy download en_core_web_sm')
    nlp = spacy.load('en_core_web_sm')


class ResumeParser:
    """Class to parse resume documents and extract structured information."""
    
    # Section headers commonly found in resumes
    SECTION_HEADERS = {
        'education': ['education', 'academic background', 'academic history', 'academic qualification', 'qualifications'],
        'experience': ['experience', 'work experience', 'employment history', 'work history', 'professional experience'],
        'skills': ['skills', 'technical skills', 'core competencies', 'competencies', 'key skills'],
        'projects': ['projects', 'project experience', 'academic projects', 'personal projects'],
        'certifications': ['certifications', 'certificates', 'professional certifications'],
        'awards': ['awards', 'honors', 'achievements', 'recognitions'],
        'publications': ['publications', 'research', 'papers', 'articles'],
        'languages': ['languages', 'language proficiency'],
        'interests': ['interests', 'hobbies', 'activities'],
        'summary': ['summary', 'professional summary', 'profile', 'objective', 'about me']
    }
    
    def __init__(self):
        """Initialize the ResumeParser."""
        self.resume_text = ""
        self.resume_sections = {}
        self.parsed_data = {}
    
    def parse(self, file_path):
        """Parse the resume file and extract structured information.
        
        Args:
            file_path (str): Path to the resume file (PDF or DOCX)
            
        Returns:
            dict: Structured resume information
        """
        # Extract text from the resume file
        self.resume_text = self._extract_text(file_path)
        
        # Split the resume into sections
        self._split_into_sections()
        
        # Extract structured information from each section
        self._extract_education()
        self._extract_experience()
        self._extract_skills()
        self._extract_projects()
        self._extract_awards()
        self._extract_summary()
        
        return self.parsed_data
    
    def _extract_text(self, file_path):
        """Extract text from a PDF or DOCX file.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            str: Extracted text
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.pdf':
            return self._extract_text_from_pdf(file_path)
        elif file_ext == '.docx':
            return self._extract_text_from_docx(file_path)
        elif file_ext == '.md':
            return self._extract_text_from_markdown(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}. Please provide a PDF, DOCX, or MD file.")
    
    def _extract_text_from_pdf(self, pdf_path):
        """Extract text from a PDF file.
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            str: Extracted text
        """
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n\n"
        return text
    
    def _extract_text_from_docx(self, docx_path):
        """Extract text from a DOCX file.
        
        Args:
            docx_path (str): Path to the DOCX file
            
        Returns:
            str: Extracted text
        """
        doc = docx.Document(docx_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
        
    def _extract_text_from_markdown(self, md_path):
        """Extract text from a Markdown file.
        
        Args:
            md_path (str): Path to the Markdown file
            
        Returns:
            str: Extracted text
        """
        with open(md_path, 'r', encoding='utf-8') as file:
            text = file.read()
        
        # Remove Markdown formatting (basic cleaning)
        # Remove headers
        text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
        # Remove bold/italic
        text = re.sub(r'\*\*|\*|__|\_', '', text)
        # Remove links but keep the text
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        # Remove code blocks
        text = re.sub(r'```[\s\S]*?```', '', text)
        # Remove inline code
        text = re.sub(r'`([^`]+)`', r'\1', text)
        
        return text
    
    def _split_into_sections(self):
        """Split the resume text into sections based on common section headers."""
        # Convert text to lowercase for easier matching
        text_lower = self.resume_text.lower()
        
        # Find potential section headers
        lines = self.resume_text.split('\n')
        section_positions = []
        
        for i, line in enumerate(lines):
            line_lower = line.strip().lower()
            # Check if this line matches any section header
            for section, headers in self.SECTION_HEADERS.items():
                if any(header == line_lower or header in line_lower for header in headers):
                    section_positions.append((i, section))
        
        # Sort section positions by line number
        section_positions.sort(key=lambda x: x[0])
        
        # Extract content for each section
        for i in range(len(section_positions)):
            current_pos, current_section = section_positions[i]
            
            # Determine the end of this section (start of next section or end of document)
            if i < len(section_positions) - 1:
                next_pos = section_positions[i + 1][0]
            else:
                next_pos = len(lines)
            
            # Extract the section content
            section_content = '\n'.join(lines[current_pos + 1:next_pos]).strip()
            self.resume_sections[current_section] = section_content
    
    def _extract_education(self):
        """Extract education information from the education section."""
        if 'education' not in self.resume_sections:
            self.parsed_data['education'] = []
            return
        
        education_text = self.resume_sections['education']
        education_entries = []
        
        # Split into paragraphs (each paragraph might be a different education entry)
        paragraphs = education_text.split('\n\n')
        
        for paragraph in paragraphs:
            if not paragraph.strip():
                continue
                
            entry = {}
            
            # Try to extract degree
            degree_patterns = [
                r'(Bachelor|Master|Ph\.?D\.?|B\.?S\.?|M\.?S\.?|B\.?A\.?|M\.?A\.?|M\.?B\.?A\.?)[^,\.]*',
                r'(Associate|Diploma|Certificate)[^,\.]*'
            ]
            
            for pattern in degree_patterns:
                match = re.search(pattern, paragraph, re.IGNORECASE)
                if match:
                    entry['degree'] = match.group(0).strip()
                    break
            
            # Try to extract university/institution
            university_patterns = [
                r'(University|College|Institute|School) of [^,\.\n]*',
                r'[^,\.\n]*(University|College|Institute|School)'
            ]
            
            for pattern in university_patterns:
                match = re.search(pattern, paragraph, re.IGNORECASE)
                if match:
                    entry['institution'] = match.group(0).strip()
                    break
            
            # Try to extract graduation date
            date_pattern = r'(19|20)\d{2}\s*(-|–|to)?\s*(19|20)?\d{0,2}|\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* (19|20)\d{2}'
            match = re.search(date_pattern, paragraph)
            if match:
                entry['date'] = match.group(0).strip()
            
            # Try to extract GPA if present
            gpa_pattern = r'GPA[:\s]*([0-9]\.[0-9]+)'
            match = re.search(gpa_pattern, paragraph, re.IGNORECASE)
            if match:
                entry['gpa'] = match.group(1)
            
            # Add the full text for reference
            entry['full_text'] = paragraph.strip()
            
            if entry:  # Only add if we extracted something
                education_entries.append(entry)
        
        self.parsed_data['education'] = education_entries
    
    def _extract_experience(self):
        """Extract work experience information from the experience section."""
        if 'experience' not in self.resume_sections:
            self.parsed_data['experience'] = []
            return
        
        experience_text = self.resume_sections['experience']
        experience_entries = []
        
        # Split into paragraphs (each paragraph might be a different experience entry)
        paragraphs = re.split(r'\n\s*\n', experience_text)
        
        for paragraph in paragraphs:
            if not paragraph.strip():
                continue
                
            entry = {}
            
            # Try to extract company name (often at the beginning of the paragraph)
            lines = paragraph.split('\n')
            if lines:
                entry['company'] = lines[0].strip()
            
            # Try to extract job title
            job_title_patterns = [
                r'(Senior|Junior|Lead|Principal|Staff)? ?(Software|Systems|Data|Full[- ]Stack|Front[- ]End|Back[- ]End|DevOps|Cloud|Machine Learning|AI)? ?(Engineer|Developer|Scientist|Analyst|Architect|Designer|Consultant|Manager|Director)',
                r'(Project|Product|Program|Technical) (Manager|Lead|Director)'
            ]
            
            for pattern in job_title_patterns:
                match = re.search(pattern, paragraph, re.IGNORECASE)
                if match:
                    entry['title'] = match.group(0).strip()
                    break
            
            # Try to extract dates
            date_pattern = r'(19|20)\d{2}\s*(-|–|to)?\s*(19|20)?\d{0,2}|\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* (19|20)\d{2}\s*(-|–|to)?\s*((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* (19|20)\d{2}|Present|Current)'
            match = re.search(date_pattern, paragraph)
            if match:
                entry['date'] = match.group(0).strip()
            
            # Extract bullet points
            bullet_points = []
            for line in lines:
                line = line.strip()
                if line.startswith(('•', '-', '*', '○', '▪', '▫', '◦', '◘', '◙', '■', '□', '▣', '▢', '▤', '▥', '▦', '▧', '▨', '▩', '◆', '◇', '◈', '◉', '◊', '○', '◌', '◍', '◎', '●', '◐', '◑', '◒', '◓', '◔', '◕', '◖', '◗', '◘', '◙', '◚', '◛', '◜', '◝', '◞', '◟', '◠', '◡', '◢', '◣', '◤', '◥', '◦', '◧', '◨', '◩', '◪', '◫', '◬', '◭', '◮', '◯', '◰', '◱', '◲', '◳', '◴', '◵', '◶', '◷', '◸', '◹', '◺', '◻', '◼', '◽', '◾', '◿')):
                    bullet_points.append(line)
            
            if bullet_points:
                entry['bullet_points'] = bullet_points
            
            # Add the full text for reference
            entry['full_text'] = paragraph.strip()
            
            if entry:  # Only add if we extracted something
                experience_entries.append(entry)
        
        self.parsed_data['experience'] = experience_entries
    
    def _extract_skills(self):
        """Extract skills from the skills section."""
        if 'skills' not in self.resume_sections:
            self.parsed_data['skills'] = []
            return
        
        skills_text = self.resume_sections['skills']
        skills = []
        
        # For Markdown files, look for specific patterns in the skills section
        programming_langs_match = re.search(r'Programming Languages:[\s\S]*?(?=\n\n|$)', skills_text)
        frameworks_match = re.search(r'Frameworks & Technologies:[\s\S]*?(?=\n\n|$)', skills_text)
        expertise_match = re.search(r'Areas of Expertise:[\s\S]*?(?=\n\n|$)', skills_text)
        
        all_skills = []
        
        # Process programming languages
        if programming_langs_match:
            langs_text = programming_langs_match.group(0)
            # Extract proficiency levels and languages
            proficiency_patterns = [r'Proficient:\s*([^\n]+)', r'Intermediate:\s*([^\n]+)', r'Familiar:\s*([^\n]+)']
            for pattern in proficiency_patterns:
                match = re.search(pattern, langs_text)
                if match:
                    langs = match.group(1).strip()
                    all_skills.extend([lang.strip() for lang in re.split(r',\s*', langs)])
        
        # Process frameworks and technologies
        if frameworks_match:
            frameworks_text = frameworks_match.group(0)
            # Extract categories and technologies
            category_pattern = r'(?:Frontend|Backend|Mobile|Cloud & DevOps|Databases|Tools):\s*([^\n]+)'  
            for match in re.finditer(category_pattern, frameworks_text):
                techs = match.group(1).strip()
                all_skills.extend([tech.strip() for tech in re.split(r',\s*', techs)])
        
        # Process areas of expertise
        if expertise_match:
            expertise_text = expertise_match.group(0)
            expertise_items = re.findall(r'- ([^\n]+)', expertise_text)
            all_skills.extend([item.strip() for item in expertise_items])
        
        # If no specific patterns were found, fall back to the original method
        if not all_skills:
            # Split by common delimiters
            for delimiter in ['•', ',', '|', '\n', ';']:
                if delimiter in skills_text:
                    skills = [skill.strip() for skill in skills_text.split(delimiter) if skill.strip()]
                    break
            
            # If no delimiter was found, use the whole text
            if not skills:
                skills = [skills_text.strip()]
            
            all_skills = skills
        
        # Use NLP to extract skill entities
        extracted_skills = set()
        for skill in all_skills:
            # Remove any remaining markdown formatting
            skill = re.sub(r'\*\*|\*|__|\\_|`|\[|\]|\(|\)|#', '', skill).strip()
            if not skill:
                continue
                
            doc = nlp(skill)
            # Extract noun phrases as potential skills
            for chunk in doc.noun_chunks:
                extracted_skills.add(chunk.text.strip())
            # Also add the original skill text
            extracted_skills.add(skill.strip())
        
        self.parsed_data['skills'] = list(extracted_skills)
    
    def _extract_projects(self):
        """Extract project information from the projects section."""
        if 'projects' not in self.resume_sections:
            self.parsed_data['projects'] = []
            return
        
        projects_text = self.resume_sections['projects']
        project_entries = []
        
        # Split into paragraphs (each paragraph might be a different project)
        paragraphs = re.split(r'\n\s*\n', projects_text)
        
        for paragraph in paragraphs:
            if not paragraph.strip():
                continue
                
            entry = {}
            
            # Try to extract project name (often at the beginning of the paragraph)
            lines = paragraph.split('\n')
            if lines:
                entry['name'] = lines[0].strip()
            
            # Extract bullet points
            bullet_points = []
            for line in lines[1:]:  # Skip the first line (project name)
                line = line.strip()
                if line.startswith(('•', '-', '*', '○', '▪', '▫', '◦')):
                    bullet_points.append(line)
            
            if bullet_points:
                entry['bullet_points'] = bullet_points
            
            # Add the full text for reference
            entry['full_text'] = paragraph.strip()
            
            if entry:  # Only add if we extracted something
                project_entries.append(entry)
        
        self.parsed_data['projects'] = project_entries
    
    def _extract_awards(self):
        """Extract awards and achievements information."""
        if 'awards' not in self.resume_sections:
            self.parsed_data['awards'] = []
            return
        
        awards_text = self.resume_sections['awards']
        award_entries = []
        
        # Split by bullet points or new lines
        lines = []
        for line in awards_text.split('\n'):
            line = line.strip()
            if line.startswith(('•', '-', '*', '○', '▪', '▫', '◦')):
                lines.append(line)
            elif line:  # If it's not a bullet point but not empty
                lines.append(line)
        
        for line in lines:
            if line.strip():
                award_entries.append(line.strip())
        
        self.parsed_data['awards'] = award_entries
    
    def _extract_summary(self):
        """Extract summary or objective information."""
        if 'summary' not in self.resume_sections:
            self.parsed_data['summary'] = ""
            return
        
        summary_text = self.resume_sections['summary']
        self.parsed_data['summary'] = summary_text.strip()