from django.db import models
from decimal import Decimal

from accounts.models import WholesalerProfile, RetailerProfile

from products.models import Product
from orders.models import Order
from coustomers.models import Customer
# Create your models here.

class Invoice(models.Model):

    STATUS_CHOICES = [
        ("UNPAID", "Unpaid"),
        ("PARTIALLY_PAID", "Partially Paid"),
        ("PAID", "Paid"),
        ("CANCELLED", "Cancelled"),
    ]

    invoice_number = models.CharField(
        max_length=30,
        unique=True
    )

    order = models.OneToOneField(
        Order,
        on_delete=models.PROTECT,
        related_name="invoice"
    )

    wholesaler = models.ForeignKey(
        WholesalerProfile,
        on_delete=models.PROTECT,
        related_name="invoices"
    )

    retailer = models.ForeignKey(
        RetailerProfile,
        on_delete=models.PROTECT,
        related_name="invoices"
    )

    invoice_date = models.DateTimeField(
        auto_now_add=True
    )

    subtotal = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0
    )

    discount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    tax_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    grand_total = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="UNPAID"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.invoice_number

    @property
    def total_paid(self):
        return sum((p.amount for p in self.payments.all()), Decimal("0.00"))

    @property
    def outstanding_amount(self):
        return max(Decimal("0.00"), self.grand_total - self.total_paid)


class InvoiceItem(models.Model):

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    price_per_unit = models.DecimalField(
        max_digits=14,
        decimal_places=2
    )

    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    tax_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    total_price = models.DecimalField(
        max_digits=14,
        decimal_places=2
    )

    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.product.name}"

class CustomerInvoice(models.Model):
    STATUS_CHOICES = [
        ("UNPAID", "Unpaid"),
        ("PARTIALLY_PAID", "Partially Paid"),
        ("PAID", "Paid"),
        ("CANCELLED", "Cancelled"),
    ]
    PAYMENT_METHOD_CHOICES = [
        ("CASH", "Cash"),
        ("UPI", "UPI"),
        ("CARD", "Card"),
        ("BANK_TRANSFER", "Bank Transfer"),
        ("OTHER", "Other"),
    ]

    invoice_number = models.CharField(max_length=50, unique=True)
    retailer = models.ForeignKey(RetailerProfile, on_delete=models.PROTECT, related_name="customer_invoices")
    
    # Customer details stored directly on the invoice
    customer_name = models.CharField(max_length=200, default="")
    customer_phone = models.CharField(max_length=20, blank=True, null=True)
    billing_address = models.TextField(blank=True, null=True)
    shipping_address = models.TextField(blank=True, null=True)

    
    invoice_date = models.DateTimeField(auto_now_add=True)
    payment_due = models.CharField(max_length=50, default="On Receipt")
    
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_discount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    cgst_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    sgst_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    round_off = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHOD_CHOICES, default="CASH")
    amount_paid = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    balance_due = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    upi_details = models.CharField(max_length=100, blank=True, null=True, default="abc@upi")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PAID")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.invoice_number} - {self.customer_name}"

class CustomerInvoiceItem(models.Model):
    invoice = models.ForeignKey(CustomerInvoice, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=255, default="")

    hsn_code = models.CharField(max_length=20, blank=True, null=True, default="6109")
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.product_name}"