from django.contrib import admin

from .models import Invoice, InvoiceItem, CustomerInvoice, CustomerInvoiceItem

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

@admin.register(CustomerInvoice)
class CustomerInvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_number",
        "customer",
        "retailer",
        "invoice_date",
        "grand_total",
        "status",
    )
    list_filter = ("status", "invoice_date",)
    search_fields = ("invoice_number", "customer__name", "retailer__shop_name",)

@admin.register(CustomerInvoiceItem)
class CustomerInvoiceItemAdmin(admin.ModelAdmin):
    list_display = (
        "invoice",
        "product",
        "quantity",
        "price_per_unit",
        "tax_rate",
        "tax_amount",
        "total_price",
    )