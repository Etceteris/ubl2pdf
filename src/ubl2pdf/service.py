"""Service applicatif de conversion XML -> PDF."""

from pathlib import Path

from ubl2pdf.parser import parse_invoice
from ubl2pdf.renderer import render_pdf


def convert(xml_path: Path, output_path: Path | None = None) -> Path:
    """Convertit une facture UBL en PDF et retourne le chemin généré."""
    xml_path = xml_path.expanduser().resolve()
    if not xml_path.is_file():
        raise FileNotFoundError(f"Fichier XML introuvable : {xml_path}")

    destination = (output_path or xml_path.with_suffix(".pdf")).expanduser().resolve()
    invoice = parse_invoice(xml_path)
    return render_pdf(invoice, destination)
