#!/usr/bin/env python3
"""
Convert Markdown to PDF using fpdf2.
"""

import re
import sys
from pathlib import Path
from fpdf import FPDF


class MarkdownToPDF(FPDF):
    """Custom PDF class for markdown conversion."""
    
    def __init__(self):
        super().__init__()
        self.add_page()
        self.set_auto_page_break(auto=True, margin=15)
        
    def header(self):
        """Add header to each page."""
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, 'Q&A Practice Application - Architecture Documentation', 0, 0, 'C')
        self.ln(15)
        
    def footer(self):
        """Add footer to each page."""
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
        
    def chapter_title(self, title, level=1):
        """Add a chapter title."""
        sizes = {1: 18, 2: 14, 3: 12, 4: 11}
        size = sizes.get(level, 11)
        
        self.set_font('Helvetica', 'B', size)
        self.set_text_color(0, 51, 102)
        self.ln(5)
        self.multi_cell(0, 8, title)
        self.ln(3)
        self.set_text_color(0, 0, 0)
        
    def body_text(self, text):
        """Add body text."""
        self.set_font('Helvetica', '', 10)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 5, text)
        self.ln(2)
        
    def code_block(self, code):
        """Add a code block."""
        self.set_font('Courier', '', 8)
        self.set_fill_color(245, 245, 245)
        self.set_text_color(51, 51, 51)
        
        # Split code into lines and add each
        lines = code.strip().split('\n')
        for line in lines:
            # Truncate long lines
            if len(line) > 90:
                line = line[:87] + '...'
            self.cell(0, 4, '  ' + line, 0, 1, fill=True)
        
        self.ln(3)
        self.set_text_color(0, 0, 0)
        
    def bullet_point(self, text, indent=0):
        """Add a bullet point."""
        self.set_font('Helvetica', '', 10)
        prefix = '  ' * indent + '- '
        self.multi_cell(0, 5, prefix + text)
        
    def table_row(self, cells, is_header=False):
        """Add a table row."""
        if is_header:
            self.set_font('Helvetica', 'B', 9)
            self.set_fill_color(230, 230, 230)
        else:
            self.set_font('Helvetica', '', 9)
            self.set_fill_color(255, 255, 255)
            
        col_width = (self.w - 20) / len(cells)
        for cell in cells:
            # Truncate long cells
            if len(cell) > 30:
                cell = cell[:27] + '...'
            self.cell(col_width, 6, cell, 1, 0, 'L', fill=is_header)
        self.ln()


def sanitize_text(text):
    """Remove or replace Unicode characters that can't be rendered."""
    replacements = {
        '✅': '[OK]',
        '🟢': '[LOW]',
        '🟡': '[MED]',
        '🟠': '[HIGH]',
        '🔴': '[CRIT]',
        '•': '-',
        '→': '->',
        '←': '<-',
        '▼': 'v',
        '▲': '^',
        '─': '-',
        '│': '|',
        '┌': '+',
        '┐': '+',
        '└': '+',
        '┘': '+',
        '├': '+',
        '┤': '+',
        '┬': '+',
        '┴': '+',
        '┼': '+',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def parse_markdown(md_content):
    """Parse markdown content and return structured data."""
    md_content = sanitize_text(md_content)
    lines = md_content.split('\n')
    elements = []
    in_code_block = False
    code_buffer = []
    in_table = False
    table_buffer = []
    
    for line in lines:
        # Code blocks
        if line.strip().startswith('```'):
            if in_code_block:
                elements.append(('code', '\n'.join(code_buffer)))
                code_buffer = []
                in_code_block = False
            else:
                in_code_block = True
            continue
            
        if in_code_block:
            code_buffer.append(line)
            continue
            
        # Tables
        if '|' in line and not line.strip().startswith('#'):
            if line.strip().startswith('|--') or line.strip().startswith('| --'):
                continue  # Skip separator line
            cells = [c.strip() for c in line.split('|') if c.strip()]
            if cells:
                if not in_table:
                    in_table = True
                    elements.append(('table_header', cells))
                else:
                    elements.append(('table_row', cells))
            continue
        else:
            in_table = False
            
        # Headers
        if line.startswith('# '):
            elements.append(('h1', line[2:].strip()))
        elif line.startswith('## '):
            elements.append(('h2', line[3:].strip()))
        elif line.startswith('### '):
            elements.append(('h3', line[4:].strip()))
        elif line.startswith('#### '):
            elements.append(('h4', line[5:].strip()))
        # Bullet points
        elif line.strip().startswith('- '):
            text = line.strip()[2:]
            # Remove markdown formatting
            text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
            text = re.sub(r'\*(.+?)\*', r'\1', text)
            text = re.sub(r'`(.+?)`', r'\1', text)
            elements.append(('bullet', text))
        # Horizontal rule
        elif line.strip() == '---':
            elements.append(('hr', ''))
        # Regular text
        elif line.strip():
            # Remove markdown formatting
            text = re.sub(r'\*\*(.+?)\*\*', r'\1', line)
            text = re.sub(r'\*(.+?)\*', r'\1', text)
            text = re.sub(r'`(.+?)`', r'\1', text)
            elements.append(('text', text.strip()))
            
    return elements


def convert_md_to_pdf(md_path, pdf_path):
    """Convert markdown file to PDF."""
    # Read markdown content
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Parse markdown
    elements = parse_markdown(md_content)
    
    # Create PDF
    pdf = MarkdownToPDF()
    
    for elem_type, content in elements:
        try:
            if elem_type == 'h1':
                pdf.chapter_title(content, 1)
            elif elem_type == 'h2':
                pdf.chapter_title(content, 2)
            elif elem_type == 'h3':
                pdf.chapter_title(content, 3)
            elif elem_type == 'h4':
                pdf.chapter_title(content, 4)
            elif elem_type == 'text':
                pdf.body_text(content)
            elif elem_type == 'bullet':
                pdf.bullet_point(content)
            elif elem_type == 'code':
                pdf.code_block(content)
            elif elem_type == 'table_header':
                pdf.table_row(content, is_header=True)
            elif elem_type == 'table_row':
                pdf.table_row(content, is_header=False)
            elif elem_type == 'hr':
                pdf.ln(5)
                pdf.set_draw_color(200, 200, 200)
                pdf.line(10, pdf.get_y(), pdf.w - 10, pdf.get_y())
                pdf.ln(5)
        except Exception as e:
            print(f"Warning: Could not render element {elem_type}: {e}")
            continue
    
    # Save PDF
    pdf.output(pdf_path)
    print(f"PDF created successfully: {pdf_path}")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python md_to_pdf.py <input.md> <output.pdf>")
        sys.exit(1)
        
    md_path = Path(sys.argv[1])
    pdf_path = Path(sys.argv[2])
    
    if not md_path.exists():
        print(f"Error: Input file not found: {md_path}")
        sys.exit(1)
        
    convert_md_to_pdf(md_path, pdf_path)
