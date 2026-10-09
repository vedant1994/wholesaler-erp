from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_name",
            "quantity",
            "price_per_unit",
            "total_price",
        ]
        read_only_fields = ["id", "product_name", "price_per_unit", "total_price"]


class OrderSerializer(serializers.ModelSerializer):
    retailer_shop_name = serializers.CharField(source="retailer.shop_name", read_only=True)
    wholesaler_business_name = serializers.CharField(source="wholesaler.business_name", read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "retailer",
            "retailer_shop_name",
            "wholesaler",
            "wholesaler_business_name",
            "status",
            "order_date",
            "notes",
            "items",
        ]
        read_only_fields = ["id", "retailer", "retailer_shop_name", "wholesaler_business_name", "status", "order_date", "items"]
