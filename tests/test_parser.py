from decimal import Decimal
from pathlib import Path

from ubl2pdf.parser import parse_invoice

FIXTURE = Path(__file__).parent / "fixtures" / "6280310.xml"


def test_parse_complete_invoice() -> None:
    invoice = parse_invoice(FIXTURE)

    assert invoice.vizup_id == "PFAF-008"
    assert invoice.vendor_reference == "EGCFRD0014640073"
    assert invoice.invoice_number == "EGCFRD0014640073"
    assert invoice.supplier.name == "Google Cloud France SARL"
    assert invoice.customer.name == "BICAMPROD"
    assert invoice.tax_exclusive_amount == Decimal("108.79")
    assert invoice.tax_amount == Decimal("21.76")
    assert invoice.tax_inclusive_amount == Decimal("130.55")
    assert invoice.payable_amount == Decimal("130.55")
    assert len(invoice.lines) == 1
    assert invoice.lines[0].name == "Google Workspace"
    assert invoice.lines[0].vat_percent == Decimal("20")
