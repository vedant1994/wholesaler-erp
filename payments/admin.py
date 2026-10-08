from django.contrib import admin

from .models import Payment, LedgerEntry, CustomerPayment

# Register your models here.

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "invoice",
        "amount",
        "payment_method",
        "payment_date",
        "reference_number",
    )

    list_filter = (
        "payment_method",
        "payment_date",
    )

    search_fields = (
        "invoice__invoice_number",
        "reference_number",
    )

@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "retailer",
        "wholesaler",
        "entry_type",
        "amount",
        "invoice",
        "payment",
        "created_at",
    )

    list_filter = (
        "entry_type",
        "created_at",
    )

    search_fields = (
        "retailer__shop_name",
        "wholesaler__business_name",
        "invoice__invoice_number",
    )

@admin.register(CustomerPayment)
class CustomerPaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "invoice",
        "amount",
        "payment_method",
        "payment_date",
        "reference_number",
    )
    list_filter = ("payment_method", "payment_date",)
    search_fields = ("invoice__invoice_number", "reference_number",)
