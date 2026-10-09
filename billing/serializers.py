from rest_framework import serializers
from .models import Invoice, InvoiceItem, CustomerInvoice, CustomerInvoiceItem


class InvoiceItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = InvoiceItem
        fields = [
            "id",
            "product",
            "product_name",
            "quantity",
            "price_per_unit",
            "tax_rate",
            "tax_amount",
            "total_price",
        ]
        read_only_fields = fields


class InvoiceSerializer(serializers.ModelSerializer):
    wholesaler_business_name = serializers.CharField(source="wholesaler.business_name", read_only=True)
    retailer_shop_name = serializers.CharField(source="retailer.shop_name", read_only=True)
    items = InvoiceItemSerializer(many=True, read_only=True)
    total_paid = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    outstanding_amount = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = Invoice
        fields = [
            "id",
            "invoice_number",
            "order",
            "wholesaler",
            "wholesaler_business_name",
            "retailer",
            "retailer_shop_name",
            "invoice_date",
            "subtotal",
            "discount",
            "tax_amount",
            "grand_total",
            "total_paid",
            "outstanding_amount",
            "status",
            "created_at",
            "items",
        ]
        read_only_fields = fields


class CustomerInvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerInvoiceItem
        fields = [
            "id",
            "product",
            "product_name",
            "hsn_code",
            "quantity",
            "unit_price",
            "discount",
            "amount",
        ]
        read_only_fields = ["id", "amount"]


class CustomerInvoiceSerializer(serializers.ModelSerializer):
    items = CustomerInvoiceItemSerializer(many=True, read_only=True)

    class Meta:
        model = CustomerInvoice
        fields = [
            "id",
            "invoice_number",
            "retailer",
            "customer_name",
            "customer_phone",
            "billing_address",
            "shipping_address",
            "invoice_date",
            "payment_due",
            "subtotal",
            "total_discount",
            "cgst_amount",
            "sgst_amount",
            "round_off",
            "grand_total",
            "payment_method",
            "amount_paid",
            "balance_due",
            "upi_details",
            "status",
            "created_at",
            "items",
        ]
        read_only_fields = ["id", "invoice_number", "retailer", "subtotal", "total_discount", "cgst_amount", "sgst_amount", "round_off", "grand_total", "amount_paid", "balance_due", "status", "created_at", "items"]
