import re
import markdown
from xhtml2pdf import pisa
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, "ICT_Challenge_AILab.md")
OUTPUT_FILE = os.path.join(BASE_DIR, "ICT_Challenge_AILab.pdf")

with open(INPUT_FILE, encoding="utf-8") as f:
    md_content = f.read()

html_body = markdown.markdown(md_content, extensions=["tables", "nl2br"])

# Voeg width-attributen toe op <th> elementen per tabel
def add_col_widths(html):
    def replace_table(m):
        table_html = m.group(0)
        col_count = len(re.findall(r'<th', table_html))
        if col_count > 0:
            pct = 100 // col_count
            table_html = re.sub(r'<th', f'<th width="{pct}%"', table_html)
        return table_html
    return re.sub(r'<table>.*?</table>', replace_table, html, flags=re.DOTALL)

html_body = add_col_widths(html_body)

html = f"""
<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<style>
  @page {{
    size: A4;
    margin: 2.2cm 2cm 2.2cm 2cm;
  }}

  body {{
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 10.5pt;
    line-height: 1.6;
    color: #1a1a1a;
  }}

  h1 {{
    font-size: 20pt;
    color: #c0392b;
    border-bottom: 3px solid #c0392b;
    padding-bottom: 6px;
    margin-bottom: 4px;
  }}

  h2 {{
    font-size: 13pt;
    color: #2c3e50;
    border-bottom: 1.5px solid #dde;
    padding-bottom: 3px;
    margin-top: 22px;
  }}

  h3 {{
    font-size: 11pt;
    color: #2c3e50;
    margin-top: 14px;
    margin-bottom: 4px;
  }}

  h4 {{
    font-size: 10.5pt;
    color: #555;
    margin-top: 10px;
    margin-bottom: 2px;
  }}

  blockquote {{
    border-left: 4px solid #c0392b;
    margin: 10px 0;
    padding: 6px 12px;
    background: #fdf6f5;
    color: #555;
    font-size: 9.5pt;
  }}

  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 9pt;
    margin: 10px 0;
  }}

  th {{
    background-color: #2c3e50;
    color: white;
    padding: 5px 6px;
    text-align: left;
  }}

  td {{
    padding: 4px 6px;
    border-bottom: 1px solid #e0e0e0;
  }}

  tr:nth-child(even) td {{
    background-color: #f7f9fb;
  }}

  ul, ol {{
    margin: 6px 0 6px 18px;
    padding: 0;
  }}

  li {{
    margin-bottom: 3px;
  }}

  code {{
    background: #f0f0f0;
    padding: 1px 4px;
    border-radius: 3px;
    font-size: 9pt;
    font-family: "Courier New", monospace;
  }}

  hr {{
    border: none;
    border-top: 1px solid #dde;
    margin: 16px 0;
  }}

  p {{
    margin: 6px 0;
  }}

  strong {{
    color: #1a1a1a;
  }}

  em {{
    color: #555;
  }}
</style>
</head>
<body>
{html_body}
</body>
</html>
"""

with open(OUTPUT_FILE, "wb") as f:
    result = pisa.CreatePDF(html, dest=f)

if result.err:
    print(f"Fout bij aanmaken PDF: {result.err}")
else:
    print(f"PDF aangemaakt: {OUTPUT_FILE}")
