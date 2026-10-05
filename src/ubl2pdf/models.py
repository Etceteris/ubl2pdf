"""Modèle métier indépendant de la représentation XML UBL."""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class Party(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str = ""
    street: str = ""
    address_line: str = ""
    postal_code: str = ""
    city: str = ""
    country: str = ""
    vat_id: str = ""
    company_id: str = ""
    endpoint_id: str = ""


class TaxSubtotal(BaseModel):
    model_config = ConfigDict(frozen=True)

    taxable_amount: Decimal
    tax_amount: Decimal
    percent: Decimal | None = None
    category_id: str = ""


class InvoiceLine(BaseModel):
    model_config = ConfigDict(frozen=True)

    line_id: str
    name: str
    description: str = ""
    seller_item_id: str = ""
    quantity: Decimal
    unit_code: str = ""
    unit_price: Decimal
    line_extension_amount: Decimal
    vat_percent: Decimal | None = None


class Invoice(BaseModel):
    """Facture normalisée extraite d'un document UBL."""

    model_config = ConfigDict(frozen=True)

    vizup_id: str
    vendor_reference: str = ""
    issue_date: date
    due_date: date | None = None
    invoice_type_code: str = ""
    currency: str = "EUR"
    buyer_reference: str = ""
    payment_means_code: str = ""
    notes: str = ""
    supplier: Party
    customer: Party
    lines: list[InvoiceLine] = Field(default_factory=list)
    taxes: list[TaxSubtotal] = Field(default_factory=list)
    tax_exclusive_amount: Decimal
    tax_amount: Decimal
    tax_inclusive_amount: Decimal
    payable_amount: Decimal

    @property
    def invoice_number(self) -> str:
        """Numéro à présenter sur le PDF : référence fournisseur, sinon identifiant VIZUP."""
        return self.vendor_reference or self.vizup_id
