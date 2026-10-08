from django.contrib import admin

from .models import Invoice, InvoiceItem

# Register your models here.

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):

    list_display = (
        "invoice_number",
        "order",
        "wholesaler",
        "retailer",
        "invoice_date",
        "grand_total",
        "status",
    )

    list_filter = (
        "status",
        "invoice_date",
    )

    search_fields = (
        "invoice_number",
        "retailer__shop_name",
        "wholesaler__business_name",
    )

@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):

    list_display = (
        "invoice",
        "product",
        "quantity",
        "price_per_unit",
        "tax_rate",
        "tax_amount",
        "total_price",
    )