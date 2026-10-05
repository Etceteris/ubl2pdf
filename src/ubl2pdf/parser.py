"""Lecture d'une facture UBL / EN16931."""

from datetime import date
from decimal import Decimal
from pathlib import Path

from lxml import etree

from ubl2pdf.constants import NS, VENDOR_REFERENCE_DESCRIPTION
from ubl2pdf.models import Invoice, InvoiceLine, Party, TaxSubtotal


def _text(node: etree._Element, path: str, default: str = "") -> str:
    value = node.findtext(path, namespaces=NS)
    return (value or default).strip()


def _decimal(value: str, default: str = "0") -> Decimal:
    return Decimal(value or default)


def _date(value: str) -> date | None:
    return date.fromisoformat(value) if value else None


def _party(root: etree._Element, base: str) -> Party:
    party = root.find(f"{base}/cac:Party", namespaces=NS)
    if party is None:
        return Party()

    return Party(
        name=_text(party, "cac:PartyName/cbc:Name")
        or _text(party, "cac:PartyLegalEntity/cbc:RegistrationName"),
        street=_text(party, "cac:PostalAddress/cbc:StreetName"),
        address_line=_text(party, "cac:PostalAddress/cac:AddressLine/cbc:Line"),
        postal_code=_text(party, "cac:PostalAddress/cbc:PostalZone"),
        city=_text(party, "cac:PostalAddress/cbc:CityName"),
        country=_text(party, "cac:PostalAddress/cac:Country/cbc:IdentificationCode"),
        vat_id=_text(party, "cac:PartyTaxScheme/cbc:CompanyID"),
        company_id=_text(party, "cac:PartyLegalEntity/cbc:CompanyID"),
        endpoint_id=_text(party, "cbc:EndpointID"),
    )


def _vendor_reference(root: etree._Element) -> str:
    for reference in root.findall("cac:AdditionalDocumentReference", namespaces=NS):
        description = _text(reference, "cbc:DocumentDescription").casefold()
        if description == VENDOR_REFERENCE_DESCRIPTION:
            return _text(reference, "cbc:ID")
    return ""


def _lines(root: etree._Element) -> list[InvoiceLine]:
    result: list[InvoiceLine] = []
    for line in root.findall("cac:InvoiceLine", namespaces=NS):
        quantity_node = line.find("cbc:InvoicedQuantity", namespaces=NS)
        quantity = _decimal(quantity_node.text.strip() if quantity_node is not None and quantity_node.text else "0")
        unit_code = quantity_node.get("unitCode", "") if quantity_node is not None else ""
        vat = _text(line, "cac:Item/cac:ClassifiedTaxCategory/cbc:Percent")
        result.append(
            InvoiceLine(
                line_id=_text(line, "cbc:ID"),
                name=_text(line, "cac:Item/cbc:Name") or _text(line, "cac:Item/cbc:Description"),
                description=_text(line, "cac:Item/cbc:Description"),
                seller_item_id=_text(line, "cac:Item/cac:SellersItemIdentification/cbc:ID"),
                quantity=quantity,
                unit_code=unit_code,
                unit_price=_decimal(_text(line, "cac:Price/cbc:PriceAmount")),
                line_extension_amount=_decimal(_text(line, "cbc:LineExtensionAmount")),
                vat_percent=_decimal(vat) if vat else None,
            )
        )
    return result


def _taxes(root: etree._Element) -> list[TaxSubtotal]:
    result: list[TaxSubtotal] = []
    for subtotal in root.findall("cac:TaxTotal/cac:TaxSubtotal", namespaces=NS):
        percent = _text(subtotal, "cac:TaxCategory/cbc:Percent")
        result.append(
            TaxSubtotal(
                taxable_amount=_decimal(_text(subtotal, "cbc:TaxableAmount")),
                tax_amount=_decimal(_text(subtotal, "cbc:TaxAmount")),
                percent=_decimal(percent) if percent else None,
                category_id=_text(subtotal, "cac:TaxCategory/cbc:ID"),
            )
        )
    return result


def parse_invoice(xml_path: Path) -> Invoice:
    """Parse un fichier UBL et retourne un modèle métier normalisé."""
    parser = etree.XMLParser(resolve_entities=False, no_network=True, remove_blank_text=False)
    root = etree.parse(str(xml_path), parser).getroot()

    issue_date = _date(_text(root, "cbc:IssueDate"))
    if issue_date is None:
        raise ValueError("Le XML ne contient pas de date de facture (cbc:IssueDate).")

    return Invoice(
        vizup_id=_text(root, "cbc:ID"),
        vendor_reference=_vendor_reference(root),
        issue_date=issue_date,
        due_date=_date(_text(root, "cbc:DueDate")),
        invoice_type_code=_text(root, "cbc:InvoiceTypeCode"),
        currency=_text(root, "cbc:DocumentCurrencyCode", "EUR"),
        buyer_reference=_text(root, "cbc:BuyerReference"),
        payment_means_code=_text(root, "cac:PaymentMeans/cbc:PaymentMeansCode"),
        notes=_text(root, "cbc:Note"),
        supplier=_party(root, "cac:AccountingSupplierParty"),
        customer=_party(root, "cac:AccountingCustomerParty"),
        lines=_lines(root),
        taxes=_taxes(root),
        tax_exclusive_amount=_decimal(_text(root, "cac:LegalMonetaryTotal/cbc:TaxExclusiveAmount")),
        tax_amount=_decimal(_text(root, "cac:TaxTotal/cbc:TaxAmount")),
        tax_inclusive_amount=_decimal(_text(root, "cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount")),
        payable_amount=_decimal(_text(root, "cac:LegalMonetaryTotal/cbc:PayableAmount")),
    )
