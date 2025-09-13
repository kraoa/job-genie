#!/usr/bin/env python3

"""
LaTeX-Style PDF Generator Module

This module generates tailored PDF resumes that match the formatting of formatted_resume.tex
with proper headings, bullet points, and professional styling.
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import HexColor, black, blue
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Line
from reportlab.graphics import renderPDF
import os
import re

class LaTeXStylePDFGenerator:
    def __init__(self, output_dir="downloads"):
        """Initialize the LaTeXStylePDFGenerator.
        
        Args:
            output_dir (str): Directory to save generated PDFs
        """
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def setup_fonts(self):
        """Setup fonts similar to the LaTeX template."""
        try:
            # Try to register system fonts
            import platform
            system = platform.system()
            
            if system == "Darwin":  # macOS
                font_paths = [
                    "/Library/Fonts/Arial Unicode MS.ttf",
                    "/System/Library/Fonts/Helvetica.ttc"
                ]
            elif system == "Windows":
                font_paths = [
                    "C:/Windows/Fonts/arial.ttf",
                    "C:/Windows/Fonts/calibri.ttf"
                ]
            else:  # Linux
                font_paths = [
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
                ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        pdfmetrics.registerFont(TTFont('UnicodeFont', font_path))
                        return True
                    except Exception as e:
                        print(f"Could not register font {font_path}: {e}")
                        continue
            return False
        except Exception as e:
            print(f"Warning: Could not setup fonts: {e}")
            return False
    
    def get_styles(self):
        """Create styles that match the LaTeX template formatting."""
        styles = getSampleStyleSheet()
        
        # Setup font support
        unicode_available = self.setup_fonts()
        base_font = 'UnicodeFont' if unicode_available else 'Helvetica'
        bold_font = 'UnicodeFont' if unicode_available else 'Helvetica-Bold'
        
        # Define colors matching the LaTeX template
        airforce_blue = HexColor('#5B9BD5')  # Similar to airforceblue in LaTeX
        dark_gray = HexColor('#2E2E2E')
        light_gray = HexColor('#666666')
        
        # Custom styles matching the LaTeX template
        custom_styles = {
            'ResumeTitle': ParagraphStyle(
                name='ResumeTitle',
                parent=styles['Title'],
                fontSize=24,
                spaceAfter=8,
                textColor=black,
                alignment=TA_CENTER,
                fontName=bold_font
            ),
            'ContactInfo': ParagraphStyle(
                name='ContactInfo',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=3,
                textColor=light_gray,
                alignment=TA_CENTER,
                fontName=base_font
            ),
            'SectionHeader': ParagraphStyle(
                name='SectionHeader',
                parent=styles['Heading2'],
                fontSize=12,
                spaceAfter=6,
                spaceBefore=12,
                textColor=airforce_blue,
                fontName=bold_font,
                leftIndent=0
            ),
            'JobTitle': ParagraphStyle(
                name='JobTitle',
                parent=styles['Normal'],
                fontSize=11,
                spaceAfter=2,
                spaceBefore=6,
                textColor=black,
                fontName=bold_font,
                leftIndent=0
            ),
            'CompanyInfo': ParagraphStyle(
                name='CompanyInfo',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=2,
                textColor=light_gray,
                fontName=base_font,
                leftIndent=0
            ),
            'JobDescription': ParagraphStyle(
                name='JobDescription',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=3,
                textColor=black,
                fontName=base_font,
                leftIndent=15,
                bulletIndent=10
            ),
            'BulletPoint': ParagraphStyle(
                name='BulletPoint',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=3,
                textColor=black,
                fontName=base_font,
                leftIndent=15,
                bulletIndent=10
            ),
            'SkillsText': ParagraphStyle(
                name='SkillsText',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=3,
                textColor=black,
                fontName=base_font,
                leftIndent=0
            ),
            'ProjectTitle': ParagraphStyle(
                name='ProjectTitle',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=2,
                textColor=black,
                fontName=bold_font,
                leftIndent=0
            ),
            'ProjectDescription': ParagraphStyle(
                name='ProjectDescription',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=3,
                textColor=black,
                fontName=base_font,
                leftIndent=15,
                bulletIndent=10
            )
        }
        
        # Add custom styles to the stylesheet
        for name, style in custom_styles.items():
            if name not in styles:
                styles.add(style)
        
        return styles
    
    def create_section_header(self, title, styles):
        """Create a section header with underline like in LaTeX template."""
        # Create a drawing for the underline
        drawing = Drawing(400, 20)
        line = Line(0, 10, 400, 10)
        line.strokeColor = HexColor('#5B9BD5')
        line.strokeWidth = 1
        drawing.add(line)
        
        # Create the paragraph
        para = Paragraph(title, styles['SectionHeader'])
        
        return [para, drawing, Spacer(1, 6)]
    
    def create_job_entry(self, job, styles):
        """Create a job entry with title, company, and bullet points."""
        elements = []
        
        # Job title and company in a table format
        job_data = [
            [job.get('title', ''), job.get('duration', '')],
            [job.get('company', ''), job.get('location', '')]
        ]
        
        job_table = Table(job_data, colWidths=[4*inch, 1.5*inch])
        job_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, 0), 11),
            ('FONTNAME', (0, 1), (0, 1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (0, 1), 10),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (1, 0), (1, -1), 10),
            ('TEXTCOLOR', (0, 1), (0, 1), HexColor('#666666')),
            ('TEXTCOLOR', (1, 0), (1, -1), HexColor('#666666')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
        ]))
        
        elements.append(job_table)
        elements.append(Spacer(1, 3))
        
        # Job description bullet points
        if 'description' in job and job['description']:
            if isinstance(job['description'], list):
                for desc in job['description']:
                    if desc.strip():
                        elements.append(Paragraph(f"• {desc.strip()}", styles['JobDescription']))
            else:
                # Split by newlines and create bullet points
                descriptions = [d.strip() for d in job['description'].split('\n') if d.strip()]
                for desc in descriptions:
                    elements.append(Paragraph(f"• {desc}", styles['JobDescription']))
        
        elements.append(Spacer(1, 6))
        return elements
    
    def create_skills_section(self, skills, styles):
        """Create skills section with categories like in LaTeX template."""
        elements = []
        
        if not skills:
            return elements
        
        # Group skills by category if they're in a structured format
        if isinstance(skills, dict):
            for category, skill_list in skills.items():
                if skill_list:
                    skill_text = f"<b>{category}:</b> {', '.join(skill_list) if isinstance(skill_list, list) else skill_list}"
                    elements.append(Paragraph(skill_text, styles['SkillsText']))
                    elements.append(Spacer(1, 3))
        else:
            # Simple list of skills
            skill_text = f"<b>Technical Skills:</b> {', '.join(skills) if isinstance(skills, list) else skills}"
            elements.append(Paragraph(skill_text, styles['SkillsText']))
        
        return elements
    
    def create_education_section(self, education, styles):
        """Create education section."""
        elements = []
        
        if not education:
            return elements
        
        if isinstance(education, list):
            for edu in education:
                edu_data = [
                    [edu.get('degree', ''), edu.get('year', '')],
                    [edu.get('institution', ''), edu.get('location', '')]
                ]
                
                edu_table = Table(edu_data, colWidths=[4*inch, 1.5*inch])
                edu_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                    ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (0, 0), 11),
                    ('FONTNAME', (0, 1), (0, 1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (0, 1), 10),
                    ('TEXTCOLOR', (0, 1), (0, 1), HexColor('#666666')),
                    ('TEXTCOLOR', (1, 0), (1, -1), HexColor('#666666')),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                    ('TOPPADDING', (0, 0), (-1, -1), 2),
                ]))
                
                elements.append(edu_table)
                elements.append(Spacer(1, 6))
        else:
            # Simple education string
            elements.append(Paragraph(education, styles['JobDescription']))
        
        return elements
    
    def create_projects_section(self, projects, styles):
        """Create projects section with bullet points."""
        elements = []
        
        if not projects:
            return elements
        
        if isinstance(projects, list):
            for project in projects:
                if isinstance(project, dict):
                    title = project.get('title', '')
                    description = project.get('description', '')
                    if title:
                        elements.append(Paragraph(f"<b>{title}</b>", styles['ProjectTitle']))
                    if description:
                        if isinstance(description, list):
                            for desc in description:
                                if desc.strip():
                                    elements.append(Paragraph(f"• {desc.strip()}", styles['ProjectDescription']))
                        else:
                            elements.append(Paragraph(f"• {description}", styles['ProjectDescription']))
                    elements.append(Spacer(1, 3))
        else:
            # Simple project string
            elements.append(Paragraph(f"• {projects}", styles['ProjectDescription']))
        
        return elements
    
    def generate_pdf(self, tailored_resume, job_title, company_name):
        """Generate a PDF resume from tailored resume data.
        
        Args:
            tailored_resume (dict): Tailored resume data
            job_title (str): Job title for the resume
            company_name (str): Company name for the resume
            
        Returns:
            str: Path to the generated PDF file
        """
        # Create PDF document with margins similar to LaTeX template
        doc = SimpleDocTemplate(
            os.path.join(self.output_dir, f"{company_name}_{job_title}_resume.pdf"),
            pagesize=A4,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        styles = self.get_styles()
        story = []
        
        # Header section
        if 'name' in tailored_resume:
            story.append(Paragraph(tailored_resume['name'], styles['ResumeTitle']))
        
        # Contact information
        contact_parts = []
        if 'email' in tailored_resume:
            contact_parts.append(tailored_resume['email'])
        if 'phone' in tailored_resume:
            contact_parts.append(tailored_resume['phone'])
        if 'location' in tailored_resume:
            contact_parts.append(tailored_resume['location'])
        if 'linkedin' in tailored_resume:
            contact_parts.append(tailored_resume['linkedin'])
        if 'github' in tailored_resume:
            contact_parts.append(tailored_resume['github'])
        
        if contact_parts:
            contact_text = " ~ ".join(contact_parts)
            story.append(Paragraph(contact_text, styles['ContactInfo']))
        
        story.append(Spacer(1, 12))
        
        # Education section
        if 'education' in tailored_resume and tailored_resume['education']:
            story.extend(self.create_section_header("EDUCATION", styles))
            story.extend(self.create_education_section(tailored_resume['education'], styles))
        
        # Technical Skills section
        if 'skills' in tailored_resume and tailored_resume['skills']:
            story.extend(self.create_section_header("TECHNICAL SKILLS", styles))
            story.extend(self.create_skills_section(tailored_resume['skills'], styles))
            story.append(Spacer(1, 6))
        
        # Work Experience section
        if 'experience' in tailored_resume and tailored_resume['experience']:
            story.extend(self.create_section_header("WORK EXPERIENCE", styles))
            if isinstance(tailored_resume['experience'], list):
                for job in tailored_resume['experience']:
                    story.extend(self.create_job_entry(job, styles))
            else:
                # Simple experience string
                story.append(Paragraph(f"• {tailored_resume['experience']}", styles['JobDescription']))
        
        # Projects section
        if 'projects' in tailored_resume and tailored_resume['projects']:
            story.extend(self.create_section_header("PROJECTS", styles))
            story.extend(self.create_projects_section(tailored_resume['projects'], styles))
        
        # Awards section
        if 'awards' in tailored_resume and tailored_resume['awards']:
            story.extend(self.create_section_header("AWARDS & ACHIEVEMENTS", styles))
            if isinstance(tailored_resume['awards'], list):
                for award in tailored_resume['awards']:
                    if isinstance(award, dict):
                        title = award.get('title', '')
                        description = award.get('description', '')
                        if title:
                            story.append(Paragraph(f"<b>{title}</b>", styles['ProjectTitle']))
                        if description:
                            story.append(Paragraph(f"• {description}", styles['ProjectDescription']))
                    else:
                        story.append(Paragraph(f"• {award}", styles['ProjectDescription']))
                    story.append(Spacer(1, 3))
            else:
                story.append(Paragraph(f"• {tailored_resume['awards']}", styles['ProjectDescription']))
        
        # Build PDF
        doc.build(story)
        
        # Return the file path
        return os.path.join(self.output_dir, f"{company_name}_{job_title}_resume.pdf")
