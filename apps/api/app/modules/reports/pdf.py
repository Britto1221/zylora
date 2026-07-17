from __future__ import annotations

from io import BytesIO
from textwrap import wrap

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen.canvas import Canvas


def simple_pdf(title: str, lines: list[str]) -> bytes:
    buffer = BytesIO()
    canvas = Canvas(buffer, pagesize=A4)
    _width, height = A4
    y = height - 58
    canvas.setTitle(title)
    canvas.setFont("Helvetica-Bold", 18)
    canvas.drawString(48, y, title)
    y -= 30
    canvas.setFont("Helvetica", 9)

    for raw in lines:
        paragraphs = wrap(str(raw), 105) or [""]
        for line in paragraphs:
            if y < 52:
                canvas.showPage()
                canvas.setFont("Helvetica", 9)
                y = height - 52
            canvas.drawString(48, y, line)
            y -= 13
        y -= 4
    canvas.save()
    return buffer.getvalue()
