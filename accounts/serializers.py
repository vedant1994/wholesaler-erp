from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, WholesalerProfile, RetailerProfile, Notification


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]
        read_only_fields = ["id"]


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ["id", "user", "role", "created_at"]
        read_only_fields = fields


class WholesalerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = WholesalerProfile
        fields = [
            "id",
            "user",
            "business_name",
            "phone",
            "gst_number",
            "address",
            "city",
            "state",
            "pincode",
            "created_at",
        ]
        read_only_fields = ["id", "user", "created_at"]


class RetailerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = RetailerProfile
        fields = [
            "id",
            "user",
            "shop_name",
            "owner_name",
            "phone",
            "gst_number",
            "address",
            "city",
            "state",
            "pincode",
            "created_at",
        ]
        read_only_fields = ["id", "user", "created_at"]


class RegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=4)
    role = serializers.ChoiceField(choices=UserProfile.ROLE_CHOICES)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        return value


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "title", "message", "is_read", "created_at"]
        read_only_fields = ["id", "title", "message", "created_at"]
