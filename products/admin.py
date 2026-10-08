from django.contrib import admin
from .models import Product, Stock, RetailerStock

# Register your models here.

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "sku",
        "category",
        "unit",
        "wholesaler",
    )

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "quantity",
        "purchase_price",
        "selling_price",
        "mrp",
        "batch_number",
        "expiry_date",
        "minimum_stock",
    )

@admin.register(RetailerStock)
class RetailerStockAdmin(admin.ModelAdmin):
    list_display = (
        "retailer",
        "product",
        "quantity",
        "updated_at",
    )