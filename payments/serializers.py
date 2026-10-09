from rest_framework import serializers
from .models import Payment, LedgerEntry, CustomerPayment


class PaymentSerializer(serializers.ModelSerializer):
    invoice_number = serializers.CharField(source="invoice.invoice_number", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "invoice",
            "invoice_number",
            "amount",
            "payment_method",
            "payment_date",
            "reference_number",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "invoice_number", "payment_date", "created_at"]


class LedgerEntrySerializer(serializers.ModelSerializer):
    wholesaler_name = serializers.CharField(source="wholesaler.business_name", read_only=True)
    retailer_name = serializers.CharField(source="retailer.shop_name", read_only=True)

    class Meta:
        model = LedgerEntry
        fields = [
            "id",
            "wholesaler",
            "wholesaler_name",
            "retailer",
            "retailer_name",
            "invoice",
            "payment",
            "entry_type",
            "amount",
            "description",
            "created_at",
        ]
        read_only_fields = fields


class CustomerPaymentSerializer(serializers.ModelSerializer):
    customer_invoice_number = serializers.CharField(source="invoice.invoice_number", read_only=True)

    class Meta:
        model = CustomerPayment
        fields = [
            "id",
            "invoice",
            "customer_invoice_number",
            "amount",
            "payment_method",
            "payment_date",
            "reference_number",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "customer_invoice_number", "payment_date", "created_at"]
