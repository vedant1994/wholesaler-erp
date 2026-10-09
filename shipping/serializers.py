from rest_framework import serializers
from .models import Shipment


class ShipmentSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(source="order.id", read_only=True)

    class Meta:
        model = Shipment
        fields = [
            "id",
            "order",
            "order_id",
            "courier",
            "tracking_number",
            "shipping_date",
            "expected_delivery",
            "delivered_date",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "order_id", "created_at"]
