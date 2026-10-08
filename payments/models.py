from django.db import models

from billing.models import Invoice
from accounts.models import WholesalerProfile, RetailerProfile

# Create your models here.


class Payment(models.Model):

    PAYMENT_METHOD_CHOICES = [
        ("CASH", "Cash"),
        ("UPI", "UPI"),
        ("BANK_TRANSFER", "Bank Transfer"),
        ("CHEQUE", "Cheque"),
        ("CARD", "Card"),
        ("OTHER", "Other"),
    ]

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.PROTECT,
        related_name="payments"
    )

    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2
    )

    payment_method = models.CharField(
        max_length=30,
        choices=PAYMENT_METHOD_CHOICES
    )

    payment_date = models.DateTimeField(
        auto_now_add=True
    )

    reference_number = models.CharField(
        max_length=100,
        blank=True
    )

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"Payment #{self.id} - "
            f"{self.invoice.invoice_number}"
        )

class LedgerEntry(models.Model):

    ENTRY_TYPE_CHOICES = [
        ("DEBIT", "Debit"),
        ("CREDIT", "Credit"),
    ]

    wholesaler = models.ForeignKey(
        "accounts.WholesalerProfile",
        on_delete=models.PROTECT,
        related_name="ledger_entries"
    )

    retailer = models.ForeignKey(
        "accounts.RetailerProfile",
        on_delete = models.PROTECT,
        related_name="ledger_entries"
    )

    invoice = models.OneToOneField(
        "billing.Invoice",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="ledger_entry"
    )

    payment = models.OneToOneField(
        "payments.Payment",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="ledger_entry"
    )

    entry_type = models.CharField(
        max_length=10,
        choices=ENTRY_TYPE_CHOICES
    )

    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2
    )

    description = models.CharField(
        max_length=255,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.retailer.shop_name} - "
            f"{self.entry_type} - "
            f"₹{self.amount}"
        )