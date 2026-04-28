import os
import re
from datetime import datetime


def generate_email_pdf(email_data):
    """
    Generate a PDF from email data.
    - If HTML body exists: render it with weasyprint (preserves layout, images, links)
    - Fallback: plain text with fpdf2
    Returns the path to the generated PDF file.
    """
    output_path = f"/tmp/email_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    html_body = email_data.get('html')

    if html_body:
        return _generate_from_html(email_data, html_body, output_path)
    else:
        return _generate_from_text(email_data, output_path)


def _build_header_html(email_data):
    """Build a clean info bar to prepend at the very top of the PDF."""
    sender = email_data.get('sender', '')
    subject = email_data.get('subject', '')
    date = str(email_data.get('date', ''))
    return f"""
    <div style="
        background:#1e1e32; color:#ffffff;
        padding:12px 20px; font-family:Arial,sans-serif;
        font-size:13px; line-height:1.8;
    ">
        <strong style="font-size:16px;">📧 Email</strong><br>
        <b>From:</b> {sender}<br>
        <b>Subject:</b> {subject}<br>
        <b>Date:</b> {date}
    </div>
    <hr style="border:none;border-top:2px solid #ddd;margin:0 0 16px 0;">
    """


def _generate_from_html(email_data, html_body, output_path):
    """Use weasyprint + BeautifulSoup to render HTML email to PDF."""
    try:
        from weasyprint import HTML
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html_body, 'html.parser')

        # Collect all <style> tags from the email
        style_tags = "".join(str(tag) for tag in soup.find_all('style'))

        # Extract the <body> content (or whole doc if no body tag)
        body_tag = soup.find('body')
        body_content = str(body_tag) if body_tag else str(soup)

        # Our info header
        header_html = _build_header_html(email_data)

        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            {style_tags}
            <style>
                /* Force WeasyPrint to print all background colors and images */
                * {{
                    -webkit-print-color-adjust: exact !important;
                    print-color-adjust: exact !important;
                    color-adjust: exact !important;
                }}

                body {{ margin: 0; padding: 0; }}
                img {{ max-width: 100%; height: auto; }}

                /* Fix buttons - force background color and text to show */
                a[style*="background"], td[style*="background"],
                table[style*="background"], div[style*="background"],
                span[style*="background"] {{
                    -webkit-print-color-adjust: exact !important;
                    print-color-adjust: exact !important;
                }}
            </style>
        </head>
        <body>
            {header_html}
            {body_content}
        </body>
        </html>
        """

        HTML(string=full_html).write_pdf(output_path)
        print("  [PDF] HTML email rendered with weasyprint ✅")
        return output_path

    except Exception as e:
        print(f"  [PDF] weasyprint failed: {e}. Falling back to plain text.")
        return _generate_from_text(email_data, output_path)


def _generate_from_text(email_data, output_path):
    """Fallback: plain text PDF using fpdf2."""
    from fpdf import FPDF

    def clean(text):
        text = re.sub(r'https?://\S+', '[link]', str(text))
        return text.encode('latin-1', errors='replace').decode('latin-1')

    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(15, 15, 15)

    # Header bar
    pdf.set_fill_color(30, 30, 50)
    pdf.rect(0, 0, 210, 35, 'F')
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(15, 10)
    pdf.cell(0, 10, "Email", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_xy(15, 22)
    pdf.cell(0, 5, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.ln(20)

    # Meta fields
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(80, 80, 180)
    pdf.cell(22, 7, "From:", ln=False)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 7, clean(email_data.get('sender', '')), ln=True)

    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(80, 80, 180)
    pdf.cell(22, 7, "Subject:", ln=False)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 7, clean(email_data.get('subject', '')), ln=True)
    pdf.ln(5)

    pdf.set_draw_color(180, 180, 220)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(5)

    # Body
    pdf.set_font("Helvetica", "", 10)
    body = clean(email_data.get('body', 'No content'))
    body = re.sub(r'\n{3,}', '\n\n', body)
    pdf.multi_cell(0, 6, body)

    pdf.output(output_path)
    print("  [PDF] Plain text PDF generated ✅")
    return output_path
