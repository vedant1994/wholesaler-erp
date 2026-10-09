from rest_framework import serializers
from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    retailer_shop_name = serializers.CharField(source="retailer.shop_name", read_only=True)

    class Meta:
        model = Customer
        fields = [
            "id",
            "retailer",
            "retailer_shop_name",
            "name",
            "phone",
            "email",
            "address",
            "gst_number",
            "created_at",
        ]
        read_only_fields = ["id", "retailer", "retailer_shop_name", "created_at"]
