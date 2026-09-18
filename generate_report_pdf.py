from html import escape
from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "public" / "content" / "informe.txt"
OUTPUT = ROOT / "public" / "informe-san-martin-industria.pdf"

BLUE = colors.HexColor("#1268E8")
NAVY = colors.HexColor("#071B36")
MUTED = colors.HexColor("#5F7084")
LINE = colors.HexColor("#C8D5E3")
SOFT = colors.HexColor("#EEF4FA")


pdfmetrics.registerFont(TTFont("Nimbus", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("Nimbus-Bold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))


def draw_factory_logo(canvas, x, y, size=12):
    scale = size / 20
    points = [(3, 19), (3, 9), (8, 12), (8, 7), (13, 10), (13, 4), (17, 4), (17, 19)]
    path = canvas.beginPath()
    path.moveTo(x + points[0][0] * scale, y + (20 - points[0][1]) * scale)
    for px, py in points[1:]:
        path.lineTo(x + px * scale, y + (20 - py) * scale)
    path.close()
    canvas.drawPath(path, fill=1, stroke=0)


def page_header(canvas, doc):
    canvas.saveState()
    page_width, page_height = A4
    left = 17 * mm
    right = page_width - 17 * mm
    top = page_height - 15 * mm

    canvas.setFillColor(BLUE)
    canvas.roundRect(left, top - 12 * mm, 12 * mm, 12 * mm, 2.5 * mm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    draw_factory_logo(canvas, left + 2.1 * mm, top - 10.6 * mm, 8.2 * mm)

    canvas.setFillColor(NAVY)
    canvas.setFont("Nimbus-Bold", 8.2)
    canvas.drawString(left + 16 * mm, top - 4.4 * mm, "SAN MARTÍN")
    canvas.setFillColor(BLUE)
    canvas.drawString(left + 16 * mm, top - 8.3 * mm, "INDUSTRIA")

    author_style = ParagraphStyle(
        "HeaderAuthors",
        fontName="Nimbus-Bold",
        fontSize=7.5,
        leading=9,
        textColor=NAVY,
        alignment=TA_RIGHT,
    )
    author_text = "Carlos Brown y Luciano Jáuregui"
    block = Paragraph(author_text, author_style)
    block_width = 112 * mm
    _, block_height = block.wrap(block_width, 24 * mm)
    block.drawOn(canvas, right - block_width, top - block_height + 0.5 * mm)

    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.65)
    canvas.line(left, top - 17 * mm, right, top - 17 * mm)

    canvas.setFillColor(MUTED)
    canvas.setFont("Nimbus", 7)
    canvas.drawRightString(right, 9 * mm, f"{doc.page}")
    canvas.restoreState()


styles = getSampleStyleSheet()
title = ParagraphStyle(
    "Title",
    parent=styles["Title"],
    fontName="Nimbus-Bold",
    fontSize=25,
    leading=27,
    textColor=NAVY,
    alignment=TA_LEFT,
    spaceAfter=10,
)
lead = ParagraphStyle(
    "Lead",
    parent=styles["BodyText"],
    fontName="Nimbus",
    fontSize=12,
    leading=16,
    textColor=MUTED,
    spaceAfter=14,
)
body = ParagraphStyle(
    "Body",
    parent=styles["BodyText"],
    fontName="Nimbus",
    fontSize=9.4,
    leading=13.3,
    textColor=NAVY,
    spaceAfter=8.5,
    allowWidows=0,
    allowOrphans=0,
)
meta = ParagraphStyle(
    "Meta",
    parent=body,
    fontName="Nimbus-Bold",
    fontSize=9,
    leading=12,
    textColor=NAVY,
    spaceAfter=5,
)
author_note = ParagraphStyle(
    "AuthorNote",
    parent=body,
    fontSize=8.5,
    leading=12,
    textColor=NAVY,
    backColor=SOFT,
    borderColor=BLUE,
    borderWidth=0.7,
    borderPadding=8,
    borderRadius=0,
    spaceBefore=5,
    spaceAfter=11,
)
h2 = ParagraphStyle(
    "H2",
    parent=styles["Heading2"],
    fontName="Nimbus-Bold",
    fontSize=17,
    leading=20,
    textColor=NAVY,
    spaceBefore=16,
    spaceAfter=9,
    keepWithNext=True,
)
h3 = ParagraphStyle(
    "H3",
    parent=styles["Heading3"],
    fontName="Nimbus-Bold",
    fontSize=12.5,
    leading=15,
    textColor=NAVY,
    spaceBefore=11,
    spaceAfter=6,
    keepWithNext=True,
)
proposal = ParagraphStyle(
    "Proposal",
    parent=body,
    fontName="Nimbus-Bold",
    fontSize=9.6,
    leading=13.2,
    textColor=NAVY,
    spaceBefore=5,
    spaceAfter=6,
    keepWithNext=False,
)
table_cell = ParagraphStyle(
    "TableCell",
    parent=body,
    fontSize=7.4,
    leading=9,
    spaceAfter=0,
)
table_head = ParagraphStyle(
    "TableHead",
    parent=table_cell,
    fontName="Nimbus-Bold",
    textColor=colors.white,
)


def para(text, style=body):
    return Paragraph(escape(text).replace("\n", "<br/>"), style)


def build_story(text):
    raw = [line.strip() for line in text.replace("\ufeff", "").replace("\r", "").split("\n")]
    story = []
    pending = []

    def flush():
        if pending:
            story.append(para(" ".join(pending)))
            pending.clear()

    i = 0
    while i < len(raw):
        line = raw[i]
        if not line:
            flush()
            i += 1
            continue
        if re.fullmatch(r"_+", line):
            flush()
            story.extend([Spacer(1, 5), HRFlowable(width="100%", thickness=0.65, color=LINE), Spacer(1, 5)])
            i += 1
            continue
        if i == 0:
            flush()
            story.append(para(line, title))
            i += 1
            continue
        if i == 1:
            flush()
            story.append(para(line, lead))
            i += 1
            continue
        if line.startswith("Por Carlos Brown y Luciano Jáuregui") or line == "Movimiento Productivo Argentino / ACEP San Martín.":
            flush()
            story.append(para(line, meta))
            i += 1
            continue
        if line.startswith("* Sobre los autores."):
            flush()
            details = escape(line[len("* Sobre los autores."):].strip())
            story.append(Paragraph(f"<b>* Sobre los autores.</b> {details}", author_note))
            i += 1
            continue
        if re.match(r"^\d+\.\s", line) and len(line) >= 120:
            flush()
            story.append(para(line, proposal))
            i += 1
            continue
        if re.match(r"^\d+\.\s", line) or (re.match(r"^(Síntesis|Conclusión|Fuentes|Propuestas)", line, re.I) and len(line) < 80):
            flush()
            story.append(para(line, h2))
            i += 1
            continue
        if re.match(r"^\d+\.\d+\s", line):
            flush()
            story.append(para(line, h3))
            i += 1
            continue
        if re.fullmatch(r"Municipio|Jurisdicción|Programa|Año|Nivel|Indicador|Concepto", line, re.I):
            flush()
            rows = []
            j = i
            while j < len(raw) and raw[j] and len(rows) < 45:
                rows.append(raw[j])
                j += 1
            if len(rows) >= 6:
                columns = 2 if rows[0] == "Año" or (rows[0] == "Municipio" and len(rows) > 1 and rows[1].lower() == "variación") else 3
                data = []
                for offset in range(0, len(rows), columns):
                    cells = rows[offset:offset + columns]
                    if len(cells) < columns:
                        cells += [""] * (columns - len(cells))
                    cell_style = table_head if offset == 0 else table_cell
                    data.append([para(cell, cell_style) for cell in cells])
                widths = [doc_width / columns] * columns
                table = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
                table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, SOFT]),
                    ("GRID", (0, 0), (-1, -1), 0.35, LINE),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]))
                story.extend([Spacer(1, 6), table, Spacer(1, 10)])
                i = j
                continue
        pending.append(line)
        i += 1

    flush()
    return story


page_width, page_height = A4
doc_width = page_width - 34 * mm
doc = BaseDocTemplate(
    str(OUTPUT),
    pagesize=A4,
    leftMargin=17 * mm,
    rightMargin=17 * mm,
    topMargin=39 * mm,
    bottomMargin=17 * mm,
    title="San Martín: la capital que dejó de cuidar su industria",
    author="Carlos Brown y Luciano Jáuregui",
    subject="Diagnóstico comparado de la política productiva municipal",
)
frame = Frame(doc.leftMargin, doc.bottomMargin, doc_width, page_height - doc.topMargin - doc.bottomMargin, id="report")
doc.addPageTemplates(PageTemplate(id="report", frames=[frame], onPage=page_header))
doc.build(build_story(SOURCE.read_text(encoding="utf-8")))
print(OUTPUT)
