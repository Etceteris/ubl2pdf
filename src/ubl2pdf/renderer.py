"""Rendu PDF d'une facture normalisée."""

from decimal import Decimal
from html import escape
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from ubl2pdf.fonts import register_fonts
from ubl2pdf.models import Invoice, Party


def _money(value: Decimal, currency: str) -> str:
    formatted = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", " ")
    return f"{formatted} €" if currency == "EUR" else f"{formatted} {currency}"


def _decimal_label(value: Decimal) -> str:
    return format(value.normalize(), "f")


def _party_block(party: Party) -> str:
    lines = [f"<b>{escape(party.name)}</b>" if party.name else ""]
    lines.extend(escape(value) for value in (party.street, party.address_line) if value)
    city = " ".join(value for value in (party.postal_code, party.city) if value)
    if city:
        lines.append(escape(city))
    if party.country:
        lines.append(escape(party.country))
    if party.company_id:
        lines.append(f"SIREN : {escape(party.company_id)}")
    if party.vat_id:
        lines.append(f"TVA : {escape(party.vat_id)}")
    return "<br/>".join(line for line in lines if line)


def render_pdf(invoice: Invoice, output_path: Path) -> Path:
    """Génère un PDF lisible à partir d'un modèle :class:`Invoice`."""
    fonts = register_fonts()
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="BaseUBL",
            parent=styles["BodyText"],
            fontName=fonts.regular,
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#222222"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="SmallUBL",
            parent=styles["BodyText"],
            fontName=fonts.regular,
            fontSize=7.5,
            leading=10,
            textColor=colors.HexColor("#444444"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="TitleUBL",
            parent=styles["Title"],
            fontName=fonts.bold,
            fontSize=24,
            leading=28,
            alignment=TA_RIGHT,
            textColor=colors.HexColor("#222222"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="H2UBL",
            parent=styles["Heading2"],
            fontName=fonts.bold,
            fontSize=10,
            leading=13,
            textColor=colors.HexColor("#333333"),
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="RightUBL",
            parent=styles["BodyText"],
            fontName=fonts.regular,
            fontSize=9,
            leading=12,
            alignment=TA_RIGHT,
        )
    )
    styles.add(
        ParagraphStyle(
            name="RightBoldUBL",
            parent=styles["BodyText"],
            fontName=fonts.bold,
            fontSize=10,
            leading=13,
            alignment=TA_RIGHT,
        )
    )

    issue_date = invoice.issue_date.strftime("%d/%m/%Y")
    due_date = invoice.due_date.strftime("%d/%m/%Y") if invoice.due_date else ""
    header_details = [f"<b>N° {escape(invoice.invoice_number)}</b>"]
    if invoice.vendor_reference and invoice.vizup_id:
        header_details.append(f"Référence VIZUP : {escape(invoice.vizup_id)}")
    header_details.append(f"Date : {issue_date}")
    if due_date:
        header_details.append(f"Échéance : {due_date}")

    story: list[object] = []
    header = Table(
        [
            [Paragraph(_party_block(invoice.supplier), styles["BaseUBL"]), Paragraph("FACTURE", styles["TitleUBL"])],
            ["", Paragraph("<br/>".join(header_details), styles["RightUBL"])],
        ],
        colWidths=[110 * mm, 70 * mm],
    )
    header.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2 * mm),
            ]
        )
    )
    story.extend([header, Spacer(1, 7 * mm)])

    references = []
    if invoice.buyer_reference:
        references.append(f"Référence acheteur : {escape(invoice.buyer_reference)}")
    if invoice.vendor_reference:
        references.append(f"Référence fournisseur : {escape(invoice.vendor_reference)}")
    if invoice.payment_means_code:
        references.append(f"Code moyen de paiement : {escape(invoice.payment_means_code)}")

    info = Table(
        [
            [Paragraph("<b>FACTURÉ À</b>", styles["H2UBL"]), Paragraph("<b>RÉFÉRENCES</b>", styles["H2UBL"])],
            [
                Paragraph(_party_block(invoice.customer), styles["BaseUBL"]),
                Paragraph("<br/>".join(references), styles["BaseUBL"]),
            ],
        ],
        colWidths=[105 * mm, 75 * mm],
    )
    info.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#D0D0D0")),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#E5E5E5")),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F4F4F4")),
                ("LEFTPADDING", (0, 0), (-1, -1), 4 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 3 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3 * mm),
            ]
        )
    )
    story.extend([info, Spacer(1, 8 * mm)])

    rows = [
        [
            Paragraph("<b>Désignation</b>", styles["SmallUBL"]),
            Paragraph("<b>Référence</b>", styles["SmallUBL"]),
            Paragraph("<b>Qté</b>", styles["SmallUBL"]),
            Paragraph("<b>PU HT</b>", styles["SmallUBL"]),
            Paragraph("<b>TVA</b>", styles["SmallUBL"]),
            Paragraph("<b>Total HT</b>", styles["SmallUBL"]),
        ]
    ]
    for line in invoice.lines:
        rows.append(
            [
                Paragraph(escape(line.name), styles["BaseUBL"]),
                Paragraph(escape(line.seller_item_id), styles["BaseUBL"]),
                Paragraph(_decimal_label(line.quantity), styles["RightUBL"]),
                Paragraph(_money(line.unit_price, invoice.currency), styles["RightUBL"]),
                Paragraph(
                    f"{_decimal_label(line.vat_percent)} %" if line.vat_percent is not None else "",
                    styles["RightUBL"],
                ),
                Paragraph(_money(line.line_extension_amount, invoice.currency), styles["RightUBL"]),
            ]
        )

    items = Table(rows, colWidths=[68 * mm, 24 * mm, 13 * mm, 27 * mm, 18 * mm, 30 * mm], repeatRows=1)
    items.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EAEAEA")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D5D5D5")),
                ("LEFTPADDING", (0, 0), (-1, -1), 2.5 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2.5 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 2.5 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5 * mm),
            ]
        )
    )
    story.extend([items, Spacer(1, 6 * mm)])

    summary_rows: list[list[object]] = [
        ["", Paragraph("Total HT", styles["RightUBL"]), Paragraph(_money(invoice.tax_exclusive_amount, invoice.currency), styles["RightUBL"])]
    ]
    for tax in invoice.taxes:
        label = "TVA"
        if tax.percent is not None:
            label = f"TVA {_decimal_label(tax.percent)} %"
        summary_rows.append(
            ["", Paragraph(label, styles["RightUBL"]), Paragraph(_money(tax.tax_amount, invoice.currency), styles["RightUBL"])]
        )
    if not invoice.taxes and invoice.tax_amount:
        summary_rows.append(
            ["", Paragraph("TVA", styles["RightUBL"]), Paragraph(_money(invoice.tax_amount, invoice.currency), styles["RightUBL"])]
        )
    summary_rows.extend(
        [
            ["", Paragraph("<b>Total TTC</b>", styles["RightBoldUBL"]), Paragraph(f"<b>{_money(invoice.tax_inclusive_amount, invoice.currency)}</b>", styles["RightBoldUBL"])],
            ["", Paragraph("<b>Net à payer</b>", styles["RightBoldUBL"]), Paragraph(f"<b>{_money(invoice.payable_amount, invoice.currency)}</b>", styles["RightBoldUBL"])],
        ]
    )
    summary = Table(summary_rows, colWidths=[100 * mm, 45 * mm, 35 * mm])
    summary.setStyle(
        TableStyle(
            [
                ("LINEABOVE", (1, 0), (-1, 0), 0.5, colors.HexColor("#A0A0A0")),
                ("LINEABOVE", (1, -2), (-1, -2), 0.8, colors.HexColor("#777777")),
                ("LINEBELOW", (1, -1), (-1, -1), 0.8, colors.HexColor("#777777")),
                ("LEFTPADDING", (0, 0), (-1, -1), 2 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 2 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2 * mm),
            ]
        )
    )
    story.extend([summary, Spacer(1, 9 * mm)])

    if invoice.notes:
        notes = escape(invoice.notes).replace("\n", "<br/>")
        story.append(
            KeepTogether(
                [
                    Paragraph("Mentions / conditions", styles["H2UBL"]),
                    Paragraph(notes, styles["SmallUBL"]),
                ]
            )
        )

    story.extend(
        [
            Spacer(1, 6 * mm),
            Paragraph(
                "Document généré à partir du XML UBL / EN16931 fourni. Le XML reste la source de données.",
                styles["SmallUBL"],
            ),
        ]
    )

    def footer(canvas, doc) -> None:
        canvas.saveState()
        canvas.setFont(fonts.regular, 7)
        canvas.setFillColor(colors.HexColor("#777777"))
        canvas.drawRightString(A4[0] - 15 * mm, 10 * mm, f"Page {doc.page}")
        canvas.restoreState()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=14 * mm,
        bottomMargin=15 * mm,
        title=f"Facture {invoice.invoice_number}",
        author="ubl2pdf",
    ).build(story, onFirstPage=footer, onLaterPages=footer)

    return output_path
