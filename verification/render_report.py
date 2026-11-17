"""Render the three-page technical review from its Markdown source (ReportLab)."""
import os
import re
from html import escape
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import PageBreak, Paragraph, Preformatted, SimpleDocTemplate, Spacer, Table, TableStyle


HERE = Path(__file__).resolve().parent
FONT_DIR = Path(os.environ.get("WINDIR", "/usr/share/fonts/truetype/dejavu"))
WINDOWS = "WINDIR" in os.environ
if WINDOWS:
    FONT_DIR /= "Fonts"
for name, windows, linux in [
    ("Body", "georgia.ttf", "DejaVuSerif.ttf"),
    ("Heading", "georgiab.ttf", "DejaVuSerif-Bold.ttf"),
    ("Mono", "consola.ttf", "DejaVuSansMono.ttf"),
]:
    pdfmetrics.registerFont(TTFont(name, str(FONT_DIR / (windows if WINDOWS else linux))))
pdfmetrics.registerFontFamily("Body", normal="Body", bold="Heading")

INK = colors.HexColor("#222222")
MUTED = colors.HexColor("#515151")
RULE = colors.HexColor("#929292")
styles = {
    "body": ParagraphStyle("body", fontName="Body", fontSize=11, leading=16, spaceAfter=11, textColor=INK),
    "title": ParagraphStyle("title", fontName="Body", fontSize=23, leading=28, spaceAfter=10, textColor=INK),
    "meta": ParagraphStyle("meta", fontName="Body", fontSize=9.5, leading=12, spaceAfter=19, textColor=MUTED),
    "section": ParagraphStyle("section", fontName="Heading", fontSize=14, leading=18, spaceBefore=8,
                              spaceAfter=8, textColor=INK, keepWithNext=True),
    "caption": ParagraphStyle("caption", fontName="Body", fontSize=9.5, leading=13, spaceBefore=3,
                              spaceAfter=6, textColor=INK, keepWithNext=True),
    "cell": ParagraphStyle("cell", fontName="Body", fontSize=9, leading=12, textColor=INK),
    "header": ParagraphStyle("header", fontName="Heading", fontSize=9, leading=12, textColor=INK),
    "code": ParagraphStyle("code", fontName="Mono", fontSize=8.8, leading=13, leftIndent=9, spaceAfter=10),
}
for style in ("cell", "header"):
    styles[style + "_number"] = ParagraphStyle(style + "_number", parent=styles[style], alignment=TA_RIGHT)


def paragraph(value, style):
    value = escape(value)
    value = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<link href="\2"><u>\1</u></link>', value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", value)
    value = re.sub(r"`([^`]+)`", r'<font face="Mono">\1</font>', value)
    return Paragraph(value, styles[style])


def table(block):
    lines = [line.strip().strip("|").split("|") for line in block.splitlines()]
    def format_row(row, style):
        return [paragraph(value.strip(), style + ("_number" if index >= len(row) - 2 else ""))
                for index, value in enumerate(row)]

    headings = format_row(lines[0], "header")
    values = [format_row(row, "cell") for row in lines[2:]]
    sizes = [116, 65, 121, 80, 86] if len(headings) == 5 else [196, 133, 139]
    grid = Table([headings] + values, colWidths=sizes, hAlign="LEFT", repeatRows=1)
    grid.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (-1, 0), 0.65, INK),
        ("LINEBELOW", (0, 0), (-1, 0), 0.4, RULE),
        ("LINEBELOW", (0, -1), (-1, -1), 0.65, INK),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return [grid, Spacer(1, 14)]


def footer(canvas, doc):
    canvas.setFillColor(MUTED)
    canvas.setFont("Body", 9)
    canvas.drawRightString(540, 39, str(doc.page))


def main():
    markdown = (HERE / "TECHNICAL_REPORT.md").read_text(encoding="utf-8")
    story = []
    for block in markdown.strip().split("\n\n"):
        if block == "<!-- page -->":
            story.append(PageBreak())
        elif block.startswith("# "):
            story.append(paragraph(block[2:], "title"))
        elif block.startswith("## "):
            story.append(paragraph(block[3:], "section"))
        elif " · Independent technical review" in block:
            story.append(paragraph(block, "meta"))
        elif block.startswith("Table "):
            story.append(paragraph(block, "caption"))
        elif block.startswith("|"):
            story.extend(table(block))
        elif block.startswith("```"):
            story.append(Preformatted("\n".join(block.splitlines()[1:-1]), styles["code"]))
        else:
            story.append(paragraph(block, "body"))
    doc = SimpleDocTemplate(str(HERE / "TECHNICAL_REPORT.pdf"), pagesize=letter,
                            leftMargin=66, rightMargin=66, topMargin=66, bottomMargin=57,
                            title="Household ordering in the multilayer ERGM", invariant=1)
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    if doc.page != 3:
        raise ValueError(f"Expected three pages, generated {doc.page}")


if __name__ == "__main__":
    main()
