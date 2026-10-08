from django.db import models
from accounts.models import WholesalerProfile, RetailerProfile

# Create your models here.

class Product(models.Model):

    wholesaler = models.ForeignKey(
        WholesalerProfile,
        on_delete=models.CASCADE,
        related_name="products"
    )
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    unit = models.CharField(max_length=50)
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Stock(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="stocks"
    )
    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    purchase_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    selling_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    mrp = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    supplier = models.CharField(
        max_length=100,
        blank=True
    )
    batch_number = models.CharField(
        max_length=100,
        blank=True
    )
    expiry_date = models.DateField(
        null=True,
        blank=True
    )
    minimum_stock = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.product.name} - {self.batch_number}"

class RetailerStock(models.Model):

    retailer = models.ForeignKey(
        RetailerProfile,
        on_delete=models.CASCADE,
        related_name="stock"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="retailer_stocks"
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["retailer", "product"],
                name="unique_retailer_product_stock"
            )
        ]

    def __str__(self):
        return f"{self.retailer.shop_name} - {self.product.name}"