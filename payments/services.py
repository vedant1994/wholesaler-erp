from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from billing.models import Invoice
from .models import Payment, LedgerEntry


@transaction.atomic
def create_payment(
    invoice_id,
    amount,
    payment_method,
    reference_number="",
    notes=""
):
    invoice = (
        Invoice.objects
        .select_for_update()
        .get(id=invoice_id)
    )

    amount = Decimal(str(amount))

    if amount<=Decimal("0.00"):
        raise ValidationError(
            "payment amount must be greater than zero."
        )

    if invoice.status == "CANCELLED":
        raise ValidationError(
            "Cannot make payment for a cancelled invoice."
        )

    total_paid = sum(
        (
            payment.amount
            for payment in invoice.payments.all()
        ),
        Decimal("0.00")
    )

    outstanding = (
        invoice.grand_total-total_paid
    )

    if amount > outstanding:
        raise ValidationError(
            f"Payment exceeds outstanding amount."
            f"Outstanding amount is ₹{outstanding}."
        )

    payment = Payment.objects.create(
        invoice=invoice,
        amount=amount,
        payment_method=payment_method,
        reference_number=reference_number,
        notes=notes,
    )

    LedgerEntry.objects.create(
        wholesaler=invoice.wholesaler,
        retailer=invoice.retailer,
        payment=payment,
        entry_type="CREDIT",
        amount=payment.amount,
        description=(
            f"Payment against {invoice.invoice_number}"
        )
    )

    new_total_paid = total_paid + amount

    if new_total_paid >= invoice.grand_total:
        invoice.status = "PAID"
    else:
        invoice.status = "PARTIALLY_PAID"

    invoice.save(
        update_fields=["status"]
    )

    return payment