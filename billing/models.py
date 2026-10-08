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

    invoice_number = models.CharField(max_length=30, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="invoices")
    retailer = models.ForeignKey(RetailerProfile, on_delete=models.PROTECT, related_name="customer_invoices")
    
    invoice_date = models.DateTimeField(auto_now_add=True)
    subtotal = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="UNPAID")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.invoice_number

class CustomerInvoiceItem(models.Model):
    invoice = models.ForeignKey(CustomerInvoice, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    price_per_unit = models.DecimalField(max_digits=14, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=14, decimal_places=2)

    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.product.name}"