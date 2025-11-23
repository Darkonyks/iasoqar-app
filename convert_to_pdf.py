#!/usr/bin/env python3
"""
PDF Converter for Markdown Documentation
Converts Markdown files to PDF using markdown and weasyprint libraries.
"""

import markdown
from weasyprint import HTML, CSS
from pathlib import Path
import sys


def create_html_template(title, content):
    """Create HTML template with Serbian language support and nice styling."""
    return f"""
<!DOCTYPE html>
<html lang="sr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        @page {{
            size: A4;
            margin: 2cm 1.5cm;
            @bottom-right {{
                content: "Strana " counter(page) " od " counter(pages);
                font-size: 10pt;
                color: #666;
            }}
        }}

        body {{
            font-family: 'DejaVu Sans', Arial, sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #333;
            max-width: 100%;
        }}

        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-top: 30px;
            font-size: 24pt;
            page-break-before: auto;
        }}

        h2 {{
            color: #34495e;
            border-bottom: 2px solid #3498db;
            padding-bottom: 8px;
            margin-top: 25px;
            font-size: 18pt;
            page-break-after: avoid;
        }}

        h3 {{
            color: #2980b9;
            margin-top: 20px;
            font-size: 14pt;
            page-break-after: avoid;
        }}

        h4 {{
            color: #5499c7;
            margin-top: 15px;
            font-size: 12pt;
            page-break-after: avoid;
        }}

        p {{
            margin: 10px 0;
            text-align: justify;
        }}

        ul, ol {{
            margin: 10px 0;
            padding-left: 30px;
        }}

        li {{
            margin: 5px 0;
        }}

        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 15px 0;
            page-break-inside: auto;
        }}

        tr {{
            page-break-inside: avoid;
            page-break-after: auto;
        }}

        th {{
            background-color: #3498db;
            color: white;
            padding: 10px;
            text-align: left;
            border: 1px solid #2980b9;
            font-weight: bold;
        }}

        td {{
            padding: 8px;
            border: 1px solid #bdc3c7;
        }}

        tr:nth-child(even) {{
            background-color: #ecf0f1;
        }}

        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 10pt;
            color: #c7254e;
        }}

        pre {{
            background-color: #f8f8f8;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            overflow-x: auto;
            page-break-inside: avoid;
        }}

        pre code {{
            background: none;
            padding: 0;
            color: #333;
        }}

        blockquote {{
            border-left: 4px solid #3498db;
            margin: 15px 0;
            padding: 10px 20px;
            background-color: #f9f9f9;
            font-style: italic;
        }}

        hr {{
            border: none;
            border-top: 2px solid #3498db;
            margin: 30px 0;
        }}

        strong {{
            color: #2c3e50;
            font-weight: bold;
        }}

        em {{
            font-style: italic;
            color: #555;
        }}

        a {{
            color: #3498db;
            text-decoration: none;
        }}

        a:hover {{
            text-decoration: underline;
        }}

        .title-page {{
            text-align: center;
            padding: 100px 0;
            page-break-after: always;
        }}

        .title-page h1 {{
            font-size: 32pt;
            color: #2c3e50;
            margin-bottom: 20px;
            border: none;
        }}

        .title-page p {{
            font-size: 14pt;
            color: #7f8c8d;
            margin: 10px 0;
        }}

        .toc {{
            page-break-after: always;
        }}

        .warning {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 10px 15px;
            margin: 15px 0;
        }}

        .info {{
            background-color: #d1ecf1;
            border-left: 4px solid #17a2b8;
            padding: 10px 15px;
            margin: 15px 0;
        }}

        .success {{
            background-color: #d4edda;
            border-left: 4px solid #28a745;
            padding: 10px 15px;
            margin: 15px 0;
        }}
    </style>
</head>
<body>
    {content}
</body>
</html>
"""


def convert_markdown_to_pdf(md_file, pdf_file):
    """
    Convert a Markdown file to PDF.

    Args:
        md_file (str): Path to input Markdown file
        pdf_file (str): Path to output PDF file
    """
    print(f"Converting {md_file} to {pdf_file}...")

    # Read Markdown file
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Convert Markdown to HTML
    html_content = markdown.markdown(
        md_content,
        extensions=[
            'extra',           # Tables, fenced code blocks, etc.
            'codehilite',      # Syntax highlighting
            'toc',             # Table of contents
            'sane_lists',      # Better list handling
            'nl2br',           # Newline to <br>
        ]
    )

    # Get title from first H1 or use filename
    title = Path(md_file).stem.replace('_', ' ').title()
    if '<h1>' in html_content:
        import re
        match = re.search(r'<h1[^>]*>(.*?)</h1>', html_content)
        if match:
            title = match.group(1)

    # Create full HTML document
    full_html = create_html_template(title, html_content)

    # Convert HTML to PDF
    try:
        HTML(string=full_html).write_pdf(pdf_file)
        print(f"✓ Successfully created: {pdf_file}")
        return True
    except Exception as e:
        print(f"✗ Error creating PDF: {e}")
        return False


def main():
    """Main function to convert all documentation files."""
    base_path = Path(__file__).parent

    # Files to convert
    files_to_convert = [
        ('USER_MANUAL_DETAILED.md', 'IASOQAR_Korisnicko_Uputstvo.pdf'),
        ('USER_GUIDE_SUMMARY.md', 'IASOQAR_Brzi_Vodic.pdf'),
        ('IASOQAR_DETAILED_ANALYSIS.md', 'IASOQAR_Tehnicka_Analiza.pdf'),
    ]

    print("=" * 60)
    print("IASOQAR PDF Converter")
    print("=" * 60)
    print()

    success_count = 0
    total_count = len(files_to_convert)

    for md_file, pdf_file in files_to_convert:
        md_path = base_path / md_file
        pdf_path = base_path / pdf_file

        if not md_path.exists():
            print(f"⚠ Warning: {md_file} not found, skipping...")
            continue

        if convert_markdown_to_pdf(str(md_path), str(pdf_path)):
            success_count += 1
            # Get file size
            size_kb = pdf_path.stat().st_size / 1024
            print(f"  Size: {size_kb:.1f} KB")

        print()

    print("=" * 60)
    print(f"Conversion complete: {success_count}/{total_count} files converted successfully")
    print("=" * 60)

    return success_count == total_count


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
