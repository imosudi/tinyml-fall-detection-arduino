"""
Generate PDF version of the project technical summary from Markdown.
"""

import os
import re
from pathlib import Path
from markdown import markdown
from weasyprint import HTML, CSS

def resolve_image_paths(md_content, base_dir):
    """Convert relative image paths to absolute file:// URIs."""
    # Pattern to match markdown image links: ![alt](path)
    def replace_img_path(match):
        alt_text = match.group(1)
        img_path = match.group(2)
        
        # Skip URLs that already have a scheme (http://, file://, etc.)
        if '://' in img_path:
            return match.group(0)
        
        # Convert relative path to absolute file:// URI
        abs_path = (base_dir / img_path).resolve()
        if abs_path.exists():
            file_uri = abs_path.as_uri()
            return f"![{alt_text}]({file_uri})"
        else:
            # If file doesn't exist, use placeholder
            print(f"Warning: Image not found: {abs_path}")
            return match.group(0)
    
    # Replace all markdown image links
    updated_content = re.sub(r'!\[([^\]]*)\]\(([^\)]+)\)', replace_img_path, md_content)
    return updated_content

def markdown_to_html(md_file):
    """Convert Markdown file to HTML."""
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Resolve image paths before converting to HTML
    base_dir = Path(md_file).parent
    md_content = resolve_image_paths(md_content, base_dir)
    
    # Convert markdown to HTML
    html_content = markdown(md_content, extensions=['extra', 'codehilite'])
    
    # Wrap in HTML structure with styling
    full_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Winter Tourism Data Analysis</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 900px;
                margin: 0 auto;
                padding: 40px;
                background-color: #f9f9f9;
            }}
            h1 {{
                color: #1f4788;
                border-bottom: 3px solid #0066cc;
                padding-bottom: 10px;
                font-size: 28px;
            }}
            h2 {{
                color: #0066cc;
                margin-top: 30px;
                font-size: 22px;
            }}
            h3 {{
                color: #0099ff;
                font-size: 18px;
            }}
            strong {{
                color: #1f4788;
            }}
            ul {{
                margin: 15px 0;
            }}
            li {{
                margin: 8px 0;
            }}
            code {{
                background-color: #f4f4f4;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
            }}
            img {{
                max-width: 100%;
                height: auto;
                margin: 20px 0;
                border: 1px solid #ddd;
                border-radius: 4px;
            }}
            a {{
                color: #0066cc;
                text-decoration: none;
            }}
            a:hover {{
                text-decoration: underline;
            }}
            .footer {{
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                font-style: italic;
                color: #666;
            }}
            @page {{
                size: A4;
                margin: 2cm;
            }}
        </style>
    </head>
    <body>
        {html_content}
        <div class="footer">
            <p>Generated from Markdown on 2026-05-06 | FH Technikum Wien AI-IoT Project © [Mosudi I. O.](https://github.com/imosudi/tinyml-fall-detection-arduino)</p>
        </div>
    </body>
    </html>
    """
    
    return full_html

def generate_pdf(md_file, output_file):
    """Generate PDF from Markdown file."""
    html_content = markdown_to_html(md_file)
    
    # Create PDF from HTML
    HTML(string=html_content).write_pdf(output_file)
    print(f"PDF generated successfully: {output_file}")

if __name__ == "__main__":
    # Get the directory of this script
    script_dir = Path(__file__).parent
    
    # Create screenshots directory if it doesn't exist
    images = script_dir / "images"
    images.mkdir(exist_ok=True)
    
    # Input and output paths
    md_file = script_dir / "TECHNICAL_PROJECT_DESCRIPTION.md"
    pdf_file = script_dir / "TECHNICAL_PROJECT_DESCRIPTION.pdf"
    
    # Generate PDF
    if md_file.exists():
        try:
            generate_pdf(str(md_file), str(pdf_file))
            print(f"\n✓ PDF generated successfully: {pdf_file}")
            print(f"\n📸 To include images in the PDF:")
            print(f"   1. Place PNG/JPG images in: {images}/")
            print(f"   2. Name them:  architecture_block_diagram.png, architecture_block_diagram.svg,  SRAM_layout.png, etc.")
            print(f"   3. Re-run this script: python generate_pdf.py")
        except ImportError as e:
            print("Error: Required packages not installed.")
            print("Install with: pip install markdown weasyprint pillow")
        except Exception as e:
            print(f"Error generating PDF: {e}")
            print("Make sure all image files referenced in TECHNICAL_PROJECT_DESCRIPTION.md exist.")
    else:
        print(f"Markdown file not found: {md_file}")

