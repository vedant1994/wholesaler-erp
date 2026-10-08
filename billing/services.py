from decimal import Decimal
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.db import transaction

from orders.models import Order
from .models import Invoice, InvoiceItem
from payments.models import LedgerEntry


@transaction.atomic
def generate_invoice(order_id):

    """
    Generate an invoice for a fulfilled order
    and create its corresponding DEBIT ledger entry.
    """

    # Lock the order during invoice generation.
    order = (
        Order.objects
        .select_for_update()
        .select_related("retailer", "wholesaler")
        .prefetch_related("items__product")
        .get(id=order_id)
    )

    # Invoice can only be generated after stock fulfillment.
    if order.status not in {
        "PROCESSING",
        "SHIPPED",
        "DELIVERED",
    }:
        raise ValidationError(
            "Invoice can be generated only after order fulfillment."
        )

    # One order can have only one invoice.
    if Invoice.objects.filter(order=order).exists():
        raise ValidationError(
            "Invoice already exists for this order."
        )

    order_items = list(order.items.all())

    if not order_items:
        raise ValidationError(
            "Cannot generate invoice for an order without items."
        )

    # Calculate subtotal.
    subtotal = sum(
        (item.total_price for item in order_items),
        Decimal("0.00")
    )

    # For the first version, discount is zero.
    discount = Decimal("0.00")

    taxable_amount = subtotal - discount

    # --------------------------------------------------
    # Create invoice with temporary unique invoice number
    # --------------------------------------------------

    invoice = Invoice.objects.create(
        invoice_number=f"TEMP-{uuid4().hex}",
        order=order,
        wholesaler=order.wholesaler,
        retailer=order.retailer,
        subtotal=subtotal,
        discount=discount,
        tax_amount=Decimal("0.00"),
        grand_total=Decimal("0.00"),
    )

    # --------------------------------------------------
    # Create invoice items and calculate GST
    # --------------------------------------------------

    total_tax = Decimal("0.00")

    for item in order_items:

        line_amount = item.total_price

        tax_rate = item.product.gst_rate

        tax_amount = (
            line_amount * tax_rate / Decimal("100")
        ).quantize(Decimal("0.01"))

        InvoiceItem.objects.create(
            invoice=invoice,
            product=item.product,
            quantity=item.quantity,
            price_per_unit=item.price_per_unit,
            tax_rate=tax_rate,
            tax_amount=tax_amount,
            total_price=line_amount + tax_amount,
        )

        total_tax += tax_amount

    # --------------------------------------------------
    # Calculate final invoice total
    # --------------------------------------------------

    grand_total = taxable_amount + total_tax

    # --------------------------------------------------
    # Generate final invoice number
    # --------------------------------------------------

    invoice.invoice_number = (
        f"INV-{invoice.invoice_date.year}-{invoice.id:06d}"
    )

    invoice.tax_amount = total_tax
    invoice.grand_total = grand_total

    invoice.save(
        update_fields=[
            "invoice_number",
            "tax_amount",
            "grand_total",
        ]
    )

    # --------------------------------------------------
    # Create DEBIT ledger entry
    # --------------------------------------------------

    LedgerEntry.objects.create(
        wholesaler=invoice.wholesaler,
        retailer=invoice.retailer,
        invoice=invoice,
        entry_type="DEBIT",
        amount=invoice.grand_total,
        description=f"Invoice {invoice.invoice_number}"
    )

    return invoice