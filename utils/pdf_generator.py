#!/usr/bin/env python3

"""
PDF Generator Module

This module generates tailored PDF resumes from parsed resume data.
"""

from fpdf import FPDF
import os

class PDFGenerator:
    def __init__(self, output_dir="output"):
        """Initialize the PDFGenerator.
        
        Args:
            output_dir (str): Directory to save generated PDFs
        """
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def generate_pdf(self, tailored_resume, job_title, company_name):
        """Generate a PDF resume from tailored resume data.
        
        Args:
            tailored_resume (dict): Tailored resume data
            job_title (str): Job title for the resume
            company_name (str): Company name for the resume
            
        Returns:
            str: Path to the generated PDF file
        """
        pdf = FPDF()
        pdf.add_page()
        
        # Set up fonts
        pdf.set_font("Arial", "B", 16)
        
        # Add personal information
        if 'name' in tailored_resume:
            pdf.cell(0, 10, tailored_resume['name'], 0, 1, 'C')
        
        if 'contact' in tailored_resume:
            pdf.set_font("Arial", "", 10)
            pdf.cell(0, 5, tailored_resume['contact'], 0, 1, 'C')
        
        # Add summary
        if 'summary' in tailored_resume:
            pdf.ln(5)
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "SUMMARY", 0, 1)
            pdf.set_font("Arial", "", 10)
            pdf.multi_cell(0, 5, tailored_resume['summary'])
        
        # Add skills
        if 'skills' in tailored_resume and tailored_resume['skills']:
            pdf.ln(5)
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "SKILLS", 0, 1)
            pdf.set_font("Arial", "", 10)
            
            # Format skills as a comma-separated list
            skills_text = ", ".join(tailored_resume['skills'])
            pdf.multi_cell(0, 5, skills_text)
        
        # Add education
        if 'education' in tailored_resume and tailored_resume['education']:
            pdf.ln(5)
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "EDUCATION", 0, 1)
            
            for edu in tailored_resume['education']:
                if isinstance(edu, dict):
                    if 'institution' in edu:
                        pdf.set_font("Arial", "B", 10)
                        pdf.cell(0, 5, edu['institution'], 0, 1)
                    
                    if 'degree' in edu:
                        pdf.set_font("Arial", "", 10)
                        pdf.cell(0, 5, edu['degree'], 0, 1)
                    
                    if 'dates' in edu:
                        pdf.set_font("Arial", "I", 10)
                        pdf.cell(0, 5, edu['dates'], 0, 1)
                    
                    pdf.ln(2)
                elif isinstance(edu, str):
                    pdf.set_font("Arial", "", 10)
                    pdf.multi_cell(0, 5, edu)
                    pdf.ln(2)
        
        # Add experience
        if 'experience' in tailored_resume and tailored_resume['experience']:
            pdf.ln(5)
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "EXPERIENCE", 0, 1)
            
            for exp in tailored_resume['experience']:
                if isinstance(exp, dict):
                    if 'title' in exp:
                        pdf.set_font("Arial", "B", 10)
                        pdf.cell(0, 5, exp['title'], 0, 1)
                    
                    if 'company' in exp:
                        pdf.set_font("Arial", "", 10)
                        pdf.cell(0, 5, exp['company'], 0, 1)
                    
                    if 'dates' in exp:
                        pdf.set_font("Arial", "I", 10)
                        pdf.cell(0, 5, exp['dates'], 0, 1)
                    
                    if 'bullet_points' in exp and exp['bullet_points']:
                        pdf.ln(2)
                        pdf.set_font("Arial", "", 10)
                        for bullet in exp['bullet_points']:
                            pdf.cell(5, 5, "•", 0, 0)
                            pdf.multi_cell(0, 5, bullet)
                    
                    pdf.ln(3)
                elif isinstance(exp, str):
                    pdf.set_font("Arial", "", 10)
                    pdf.multi_cell(0, 5, exp)
                    pdf.ln(3)
        
        # Add projects
        if 'projects' in tailored_resume and tailored_resume['projects']:
            pdf.ln(5)
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "PROJECTS", 0, 1)
            
            for proj in tailored_resume['projects']:
                if isinstance(proj, dict):
                    if 'name' in proj:
                        pdf.set_font("Arial", "B", 10)
                        pdf.cell(0, 5, proj['name'], 0, 1)
                    
                    if 'description' in proj:
                        pdf.set_font("Arial", "", 10)
                        pdf.multi_cell(0, 5, proj['description'])
                    
                    if 'bullet_points' in proj and proj['bullet_points']:
                        pdf.ln(2)
                        pdf.set_font("Arial", "", 10)
                        for bullet in proj['bullet_points']:
                            pdf.cell(5, 5, "•", 0, 0)
                            pdf.multi_cell(0, 5, bullet)
                    
                    pdf.ln(3)
                elif isinstance(proj, str):
                    pdf.set_font("Arial", "", 10)
                    pdf.multi_cell(0, 5, proj)
                    pdf.ln(3)
        
        # Add awards
        if 'awards' in tailored_resume and tailored_resume['awards']:
            pdf.ln(5)
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "AWARDS & ACHIEVEMENTS", 0, 1)
            
            for award in tailored_resume['awards']:
                if isinstance(award, dict):
                    if 'title' in award:
                        pdf.set_font("Arial", "B", 10)
                        pdf.cell(0, 5, award['title'], 0, 1)
                    
                    if 'description' in award:
                        pdf.set_font("Arial", "", 10)
                        pdf.multi_cell(0, 5, award['description'])
                    
                    pdf.ln(2)
                elif isinstance(award, str):
                    pdf.set_font("Arial", "", 10)
                    pdf.multi_cell(0, 5, award)
                    pdf.ln(2)
        
        # Generate filename
        safe_job_title = job_title.replace(" ", "_").lower()
        safe_company_name = company_name.replace(" ", "_").lower()
        filename = f"{safe_company_name}_{safe_job_title}_resume.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        # Save PDF
        pdf.output(filepath)
        
        return filepath