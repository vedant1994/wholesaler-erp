from datetime import date, timedelta
from decimal import Decimal
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import F, Sum
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from products.models import Product, Stock
from orders.models import Order
from billing.models import Invoice
from payments.models import Payment

from .models import UserProfile, WholesalerProfile, RetailerProfile, Notification
from .serializers import (
    UserSerializer,
    UserProfileSerializer,
    WholesalerProfileSerializer,
    RetailerProfileSerializer,
    RegistrationSerializer,
    NotificationSerializer,
)


@api_view(["POST"])
@permission_classes([AllowAny])
def register_api(request):
    serializer = RegistrationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    username = serializer.validated_data["username"]
    email = serializer.validated_data["email"]
    password = serializer.validated_data["password"]
    role = serializer.validated_data["role"]

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )

    profile = UserProfile.objects.create(
        user=user,
        role=role
    )

    if role == "WHOLESALER":
        WholesalerProfile.objects.create(
            user=user,
            business_name=username,
            phone="",
            address="",
            city="",
            state="",
            pincode=""
        )
    elif role == "RETAILER":
        RetailerProfile.objects.create(
            user=user,
            shop_name=username,
            owner_name=username,
            phone="",
            address="",
            city="",
            state="",
            pincode=""
        )

    login(request, user)

    return Response({
        "message": "User registered and logged in successfully.",
        "user": UserSerializer(user).data,
        "role": profile.role,
    }, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([AllowAny])
def login_api(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response(
            {"error": "Both username and password are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        profile = getattr(user, "profile", None)
        role = profile.role if profile else None

        return Response({
            "message": "Login successful.",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": role,
            }
        })
    else:
        return Response(
            {"error": "Invalid username or password."},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_api(request):
    logout(request)
    return Response({"message": "Logged out successfully."})


@api_view(["GET", "PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def user_profile_api(request):
    profile = getattr(request.user, "profile", None)

    if profile is None:
        raise PermissionDenied("User profile is not configured.")

    if request.method == "GET":
        data = {
            "profile": UserProfileSerializer(profile).data,
        }
        if profile.role == "WHOLESALER":
            w_profile = getattr(request.user, "wholesaler_profile", None)
            if w_profile:
                data["business_profile"] = WholesalerProfileSerializer(w_profile).data
        elif profile.role == "RETAILER":
            r_profile = getattr(request.user, "retailer_profile", None)
            if r_profile:
                data["business_profile"] = RetailerProfileSerializer(r_profile).data
        return Response(data)

    elif request.method in ["PUT", "PATCH"]:
        partial = (request.method == "PATCH")
        if profile.role == "WHOLESALER":
            w_profile = getattr(request.user, "wholesaler_profile", None)
            if not w_profile:
                raise NotFound("Wholesaler profile not found.")
            serializer = WholesalerProfileSerializer(w_profile, data=request.data, partial=partial)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif profile.role == "RETAILER":
            r_profile = getattr(request.user, "retailer_profile", None)
            if not r_profile:
                raise NotFound("Retailer profile not found.")
            serializer = RetailerProfileSerializer(r_profile, data=request.data, partial=partial)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_stats_api(request):
    profile = getattr(request.user, "profile", None)

    if profile is None:
        raise PermissionDenied("User profile is not configured.")

    today = date.today()
    expiry_limit = today + timedelta(days=30)

    if profile.role == "WHOLESALER":
        wholesaler = request.user.wholesaler_profile
        total_products = Product.objects.filter(wholesaler=wholesaler).count()
        low_stock_count = Stock.objects.filter(
            product__wholesaler=wholesaler,
            quantity__lte=F("minimum_stock")
        ).count()
        expiring_count = Stock.objects.filter(
            product__wholesaler=wholesaler,
            expiry_date__isnull=False,
            expiry_date__gte=today,
            expiry_date__lte=expiry_limit
        ).count()
        pending_orders_count = Order.objects.filter(
            wholesaler=wholesaler,
            status="PENDING"
        ).count()
        total_retailers = wholesaler.retailers.count()

        invoices = Invoice.objects.filter(
            wholesaler=wholesaler,
            status__in=["UNPAID", "PARTIALLY_PAID"]
        ).prefetch_related("payments")
        total_outstanding = Decimal("0.00")
        for inv in invoices:
            total_paid_for_inv = sum((p.amount for p in inv.payments.all()), Decimal("0.00"))
            outstanding_for_inv = inv.grand_total - total_paid_for_inv
            if outstanding_for_inv > Decimal("0.00"):
                total_outstanding += outstanding_for_inv
            else:
                inv.status = "PAID"
                inv.save(update_fields=["status"])

        return Response({
            "role": "WHOLESALER",
            "total_products": total_products,
            "low_stock_count": low_stock_count,
            "expiring_count": expiring_count,
            "pending_orders_count": pending_orders_count,
            "total_retailers": total_retailers,
            "total_outstanding": float(total_outstanding),
        })

    elif profile.role == "RETAILER":
        retailer = request.user.retailer_profile
        total_orders = Order.objects.filter(retailer=retailer).count()
        pending_orders_count = Order.objects.filter(retailer=retailer, status="PENDING").count()
        total_spent = Payment.objects.filter(invoice__retailer=retailer).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

        unpaid_invoices = Invoice.objects.filter(
            retailer=retailer,
            status__in=["UNPAID", "PARTIALLY_PAID"]
        ).prefetch_related("payments")

        total_unpaid = Decimal("0.00")
        for inv in unpaid_invoices:
            total_paid_for_inv = sum((p.amount for p in inv.payments.all()), Decimal("0.00"))
            outstanding_for_inv = inv.grand_total - total_paid_for_inv
            if outstanding_for_inv > Decimal("0.00"):
                total_unpaid += outstanding_for_inv
            else:
                inv.status = "PAID"
                inv.save(update_fields=["status"])

        connected_wholesalers_count = retailer.wholesalers.count()

        return Response({
            "role": "RETAILER",
            "total_orders": total_orders,
            "pending_orders_count": pending_orders_count,
            "total_spent": float(total_spent),
            "total_unpaid": float(total_unpaid),
            "connected_wholesalers_count": connected_wholesalers_count,
        })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def retailer_list_api(request):
    profile = getattr(request.user, "profile", None)
    if profile and profile.role == "WHOLESALER":
        wholesaler = request.user.wholesaler_profile
        retailers = wholesaler.retailers.all()
    else:
        retailers = RetailerProfile.objects.all()

    serializer = RetailerProfileSerializer(retailers, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def notification_list_api(request):
    notifications = Notification.objects.filter(user=request.user).order_by("-created_at")
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def mark_notification_read_api(request, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
    except Notification.DoesNotExist:
        raise NotFound("Notification not found.")

    notification.is_read = True
    notification.save(update_fields=["is_read"])
    return Response(NotificationSerializer(notification).data)
