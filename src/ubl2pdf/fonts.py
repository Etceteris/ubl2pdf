"""Résolution de polices Unicode courantes sur Linux et Windows."""

from dataclasses import dataclass
from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


@dataclass(frozen=True, slots=True)
class FontNames:
    regular: str
    bold: str


def register_fonts() -> FontNames:
    candidates = [
        (
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        ),
        (Path("C:/Windows/Fonts/arial.ttf"), Path("C:/Windows/Fonts/arialbd.ttf")),
    ]

    for regular, bold in candidates:
        if regular.exists() and bold.exists():
            pdfmetrics.registerFont(TTFont("UBL2PDF-Regular", str(regular)))
            pdfmetrics.registerFont(TTFont("UBL2PDF-Bold", str(bold)))
            return FontNames("UBL2PDF-Regular", "UBL2PDF-Bold")

    return FontNames("Helvetica", "Helvetica-Bold")
