from datetime import date, timedelta
from rest_framework import serializers
from .models import Product, Stock, RetailerStock

class ProductSerializer(serializers.ModelSerializer):
    wholesaler_name = serializers.CharField(source="wholesaler.business_name", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "wholesaler_name",
            "name",
            "sku",
            "category",
            "unit",
            "gst_rate",
            "description",
            "created_at",
        ]
        read_only_fields = ["id", "wholesaler_name", "created_at"]


class StockSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    is_low_stock = serializers.SerializerMethodField()
    expiry_status = serializers.SerializerMethodField()

    class Meta:
        model = Stock
        fields = [
            "id",
            "product",
            "product_name",
            "quantity",
            "purchase_price",
            "selling_price",
            "mrp",
            "supplier",
            "batch_number",
            "expiry_date",
            "minimum_stock",
            "is_low_stock",
            "expiry_status",
            "created_at",
        ]
        read_only_fields = ["id", "product_name", "is_low_stock", "expiry_status", "created_at"]

    def get_is_low_stock(self, obj):
        return obj.quantity <= obj.minimum_stock

    def get_expiry_status(self, obj):
        if not obj.expiry_date:
            return "NO EXPIRY DATE"
        today = date.today()
        expiry_limit = today + timedelta(days=30)
        if obj.expiry_date < today:
            return "EXPIRED"
        elif obj.expiry_date <= expiry_limit:
            return "SOON EXPIRING"
        else:
            return "GOOD"


class RetailerStockSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    shop_name = serializers.CharField(source="retailer.shop_name", read_only=True)

    class Meta:
        model = RetailerStock
        fields = [
            "id",
            "retailer",
            "shop_name",
            "product",
            "product_name",
            "quantity",
            "updated_at",
        ]
        read_only_fields = ["id", "shop_name", "product_name", "updated_at"]