"""
Markdown to PDF Converter

TEST_REPORT.md를 PDF로 변환
"""
import markdown
from weasyprint import HTML
from pathlib import Path

def convert_md_to_pdf(md_file: str, pdf_file: str):
    """Convert Markdown to PDF"""
    # Read markdown
    md_path = Path(md_file).absolute()
    pdf_path = Path(pdf_file).absolute()

    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Convert to HTML
    html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])

    # Add CSS styling
    styled_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @page {{
                size: A4;
                margin: 2cm;
            }}
            body {{
                font-family: 'Noto Sans KR', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
            }}
            h1 {{
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
                page-break-before: always;
            }}
            h1:first-child {{
                page-break-before: avoid;
            }}
            h2 {{
                color: #34495e;
                border-bottom: 2px solid #95a5a6;
                padding-bottom: 5px;
                margin-top: 30px;
            }}
            h3 {{
                color: #7f8c8d;
                margin-top: 20px;
            }}
            code {{
                background-color: #f4f4f4;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
            }}
            pre {{
                background-color: #f4f4f4;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 20px 0;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
            }}
            th {{
                background-color: #3498db;
                color: white;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            ul, ol {{
                margin: 10px 0;
                padding-left: 30px;
            }}
            li {{
                margin: 5px 0;
            }}
            strong {{
                color: #2c3e50;
            }}
            .success {{
                color: #27ae60;
            }}
            .warning {{
                color: #f39c12;
            }}
            .error {{
                color: #e74c3c;
            }}
            img {{
                max-width: 100%;
                height: auto;
                margin: 20px 0;
                border: 1px solid #ddd;
                border-radius: 5px;
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    # Convert to PDF with base_url for images
    # base_url must point to the directory containing the MD file
    base_url = md_path.parent.as_uri() + '/'

    HTML(string=styled_html, base_url=base_url).write_pdf(str(pdf_path))
    print(f"✅ PDF generated: {pdf_path}")

if __name__ == "__main__":
    import sys

    # 커맨드라인 인자로 파일 경로 받기
    if len(sys.argv) >= 3:
        md_file = sys.argv[1]
        pdf_file = sys.argv[2]
    elif len(sys.argv) == 2:
        md_file = sys.argv[1]
        pdf_file = md_file.replace(".md", ".pdf")
    else:
        # 기본값
        md_file = "reports/TEST_REPORT.md"
        pdf_file = "reports/TEST_REPORT.pdf"

    print(f"Converting {md_file} to {pdf_file}...")
    convert_md_to_pdf(md_file, pdf_file)
    print(f"✅ Done! PDF saved to {pdf_file}")
