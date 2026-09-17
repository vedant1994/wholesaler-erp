from django.db import models
from accounts.models import WholesalerProfile, RetailerProfile
from products.models import Product

# Create your models here.

class Order(models.Model):

    STATUS_CHOICES = [
        ("PENDING","Pending"),
        ("ACCEPTED","Accepted"),
        ("REJECTED","Rejected"),
        ("PROCESSING","Processing"),
        ("SHIPPED","Shipped"),
        ("DELIVERED","Delivered"),
        ("CANCELLED","Cancelled"),
    ]

    retailer = models.ForeignKey(
        RetailerProfile,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    wholesaler = models.ForeignKey(
        WholesalerProfile,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    status = models.CharField(
        max_length=20,
        choices = STATUS_CHOICES,
        default="PENDING"
    )

    order_date = models.DateTimeField(
        auto_now_add=True
    )

    notes = models.TextField(
        blank=True
    )

    def __str__(self):
        return f"Order #{self.id}"

class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    price_per_unit = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"