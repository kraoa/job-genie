#!/usr/bin/env python3

import os
import sys
import argparse
from pathlib import Path
import markdown
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, HRFlowable, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import HexColor, black, blue
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Line
from reportlab.graphics import renderPDF
from html.parser import HTMLParser
import re
import unicodedata

# Emoji mappings disabled
# EMOJI_MAP = {
#     ':email:': '✉',
#     ':phone:': '☎',
#     ':location:': '📍',
#     ':linkedin:': '💼',
#     ':github:': '🔗',
#     ':website:': '🌐',
#     ':star:': '⭐',
#     ':check:': '✓',
#     ':arrow:': '→',
#     ':bullet:': '•',
#     ':diamond:': '◆',
#     ':circle:': '●',
#     ':square:': '■'
# }

def remove_emojis(text):
    """Remove emoji characters from text to prevent square boxes in PDF"""
    # Remove emoji characters using Unicode categories
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"  # dingbats
        "\U000024C2-\U0001F251"
        "\U0001F900-\U0001F9FF"  # supplemental symbols
        "\U0001FA70-\U0001FAFF"  # symbols and pictographs extended-a
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub('', text)

# ReportLab styles for professional resume
def setup_unicode_fonts():
    """Setup Unicode fonts for better character support"""
    try:
        # Try to register system fonts that support more Unicode characters
        import platform
        system = platform.system()
        
        if system == "Darwin":  # macOS
            # Try Arial Unicode MS or Helvetica
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
        print(f"Warning: Could not setup Unicode fonts: {e}")
        return False

def get_resume_styles():
    """Create custom styles for the resume."""
    styles = getSampleStyleSheet()
    
    # Setup Unicode font support
    unicode_available = setup_unicode_fonts()
    
    # Use Unicode-capable font if available, fallback to Helvetica
    if unicode_available:
        try:
            # Test if the font is actually available
            from reportlab.pdfbase.pdfmetrics import getFont
            getFont('UnicodeFont')
            base_font = 'UnicodeFont'
            bold_font = 'UnicodeFont'
        except:
            base_font = 'Helvetica'
            bold_font = 'Helvetica-Bold'
    else:
        base_font = 'Helvetica'
        bold_font = 'Helvetica-Bold'
    
    # Define custom styles with unique names
    custom_styles = {
        'ResumeTitle': ParagraphStyle(
            name='ResumeTitle',
            parent=styles['Title'],
            fontSize=24,
            spaceAfter=12,
            textColor=HexColor('#1a202c'),
            alignment=TA_CENTER,
            fontName=bold_font
        ),
        'SectionHeader': ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=6,
            spaceBefore=12,
            textColor=HexColor('#2d3748'),
            fontName=bold_font
        ),
        'SubHeader': ParagraphStyle(
            name='SubHeader',
            parent=styles['Heading3'],
            fontSize=12,
            spaceAfter=3,
            spaceBefore=6,
            textColor=HexColor('#2d3748'),
            fontName=bold_font
        ),
        'JobTitle': ParagraphStyle(
            name='JobTitle',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=2,
            textColor=HexColor('#4a5568'),
            fontName=bold_font
        ),
        'ResumeBodyText': ParagraphStyle(
            name='ResumeBodyText',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            textColor=HexColor('#2d3748'),
            alignment=TA_JUSTIFY,
            fontName=base_font
        ),
        'ContactInfo': ParagraphStyle(
            name='ContactInfo',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=3,
            textColor=HexColor('#4a5568'),
            alignment=TA_CENTER,
            fontName=base_font
        ),
        'BulletPoint': ParagraphStyle(
            name='BulletPoint',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=3,
            leftIndent=20,
            bulletIndent=10,
            textColor=HexColor('#2d3748'),
            fontName=base_font
        )
    }
    
    # Add custom styles to the stylesheet
    for name, style in custom_styles.items():
        if name not in styles:
            styles.add(style)
    
    return styles

class HTMLToReportLabParser(HTMLParser):
    """Parse HTML and convert to ReportLab elements."""
    
    def __init__(self, styles):
        super().__init__()
        self.styles = styles
        self.story = []
        self.current_text = ""
        self.current_style = 'ResumeBodyText'
        self.in_header = False
        self.header_level = 1
        self.in_paragraph = False
        self.in_list = False
        self.list_items = []
        
    def handle_starttag(self, tag, attrs):
        if tag == 'h1':
            self.in_header = True
            self.header_level = 1
            self.current_style = 'ResumeTitle'
        elif tag in ['h2', 'h3', 'h4', 'h5', 'h6']:
            self.in_header = True
            self.header_level = int(tag[1])
            if self.header_level == 2:
                self.current_style = 'SectionHeader'
            else:
                self.current_style = 'SubHeader'
        elif tag == 'p':
            self.in_paragraph = True
            self.current_style = 'ResumeBodyText'
        elif tag in ['ul', 'ol']:
            self.in_list = True
            self.list_items = []
        elif tag == 'li':
            self.current_style = 'BulletPoint'
        elif tag == 'strong':
            self.current_text += '<b>'
        elif tag == 'em':
            self.current_text += '<i>'
        elif tag == 'hr':
            # Handle horizontal rule
            if self.current_text.strip():
                self.story.append(Paragraph(self.current_text, self.styles[self.current_style]))
                self.current_text = ''
            # Add horizontal line with full width styling
            self.story.append(Spacer(1, 8))
            self.story.append(HRFlowable(width="100%", thickness=1.5, lineCap='round', color=HexColor('#34495e'), spaceBefore=4, spaceAfter=4))
            self.story.append(Spacer(1, 8))
            
    def handle_endtag(self, tag):
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            if self.current_text.strip():
                self.story.append(Paragraph(self.current_text.strip(), self.styles[self.current_style]))
                self.current_text = ""
            self.in_header = False
        elif tag == 'p':
            if self.current_text.strip():
                self.story.append(Paragraph(self.current_text.strip(), self.styles[self.current_style]))
                self.current_text = ""
            self.in_paragraph = False
        elif tag in ['ul', 'ol']:
            for item in self.list_items:
                self.story.append(Paragraph(f"• {item}", self.styles['BulletPoint']))
            self.list_items = []
            self.in_list = False
        elif tag == 'li':
            if self.current_text.strip():
                self.list_items.append(self.current_text.strip())
                self.current_text = ""
        elif tag == 'strong':
            self.current_text += '</b>'
        elif tag == 'em':
            self.current_text += '</i>'
            
    def handle_data(self, data):
        # Clean and add text data with Unicode normalization
        if data.strip():
            # Remove emoji characters to prevent square boxes
            clean_data = remove_emojis(data)
            
            # Normalize Unicode characters for better display
            normalized_data = unicodedata.normalize('NFC', clean_data)
            
            # Emoji shortcode replacement disabled
            # for shortcode, emoji in EMOJI_MAP.items():
            #     normalized_data = normalized_data.replace(shortcode, emoji)
            
            # Escape XML characters for ReportLab
            normalized_data = normalized_data.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            self.current_text += normalized_data
        else:
            self.current_text += data
        
    def get_story(self):
        # Add any remaining text
        if self.current_text.strip():
            self.story.append(Paragraph(self.current_text.strip(), self.styles[self.current_style]))
        return self.story

def html_to_reportlab(html_content):
    """Convert HTML content to ReportLab story elements."""
    styles = get_resume_styles()
    parser = HTMLToReportLabParser(styles)
    
    # Clean up HTML content
    html_content = re.sub(r'<[^>]+>', lambda m: m.group(0).lower(), html_content)
    html_content = html_content.replace('\n', ' ').replace('\r', '')
    html_content = re.sub(r'\s+', ' ', html_content)
    
    parser.feed(html_content)
    return parser.get_story()

def convert_markdown_to_pdf(input_file, output_file=None):
    """
    Convert a Markdown file to PDF with professional styling.
    
    Args:
        input_file (str): Path to the input Markdown file
        output_file (str, optional): Path to the output PDF file
    
    Returns:
        str: Path to the generated PDF file
    """
    try:
        # Validate input file
        input_path = Path(input_file)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        if not input_path.suffix.lower() in ['.md', '.markdown']:
            raise ValueError("Input file must be a Markdown file (.md or .markdown)")
        
        # Set output file path
        if output_file is None:
            output_file = input_path.with_suffix('.pdf')
        else:
            output_file = Path(output_file)
        
        # Read the markdown file
        with open(input_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # Convert markdown to HTML
        md = markdown.Markdown(extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc'
        ])
        html_content = md.convert(markdown_content)
        
        # Create complete HTML document with styling
        full_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Resume</title>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        # Create PDF using ReportLab
        doc = SimpleDocTemplate(
            str(output_file),
            pagesize=A4,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        # Convert HTML to ReportLab elements
        story = html_to_reportlab(html_content)
        doc.build(story)
        
        print(f"✅ PDF generated successfully: {output_file}")
        return str(output_file)
        
    except Exception as e:
        print(f"❌ Error converting markdown to PDF: {str(e)}")
        sys.exit(1)

def main():
    """
    Command-line interface for the Markdown to PDF converter.
    """
    parser = argparse.ArgumentParser(
        description='Convert Markdown files to professional PDFs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python md_to_pdf.py resume.md
  python md_to_pdf.py resume.md -o my_resume.pdf
  python md_to_pdf.py resume.md --output /path/to/output.pdf
        """
    )
    
    parser.add_argument(
        'input_file',
        help='Input Markdown file (.md or .markdown)'
    )
    
    parser.add_argument(
        '-o', '--output',
        dest='output_file',
        help='Output PDF file path (default: same name as input with .pdf extension)'
    )
    
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='Markdown to PDF Converter 1.0.0'
    )
    
    args = parser.parse_args()
    
    print(f"🔄 Converting {args.input_file} to PDF...")
    convert_markdown_to_pdf(args.input_file, args.output_file)

if __name__ == '__main__':
    main()