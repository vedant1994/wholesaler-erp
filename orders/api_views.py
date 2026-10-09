from decimal import Decimal
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import WholesalerProfile
from products.models import Product
from .models import Order, OrderItem
from .serializers import OrderSerializer
from .services import fulfill_order


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def order_list_create_api(request):
    profile = getattr(request.user, "profile", None)

    if profile is None:
        raise PermissionDenied("User profile is not configured.")

    if request.method == "GET":
        if profile.role == "WHOLESALER":
            orders = Order.objects.filter(wholesaler__user=request.user)
        elif profile.role == "RETAILER":
            orders = Order.objects.filter(retailer__user=request.user)
        else:
            raise PermissionDenied("You cannot access orders.")

        status_filter = request.GET.get("status", "")
        if status_filter:
            orders = orders.filter(status=status_filter)

        orders = orders.select_related("wholesaler", "retailer").prefetch_related("items__product").order_by("-order_date")
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        if profile.role != "RETAILER":
            raise PermissionDenied("Only retailers can place orders.")

        retailer = getattr(request.user, "retailer_profile", None)
        wholesaler_id = request.data.get("wholesaler")
        product_id = request.data.get("product")
        quantity = request.data.get("quantity")
        notes = request.data.get("notes", "")

        if not wholesaler_id or not product_id or not quantity:
            return Response(
                {"error": "wholesaler, product, and quantity are required fields."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            quantity = Decimal(str(quantity))
            if quantity <= 0:
                raise ValueError()
        except Exception:
            return Response({"error": "Quantity must be a positive number."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            wholesaler = WholesalerProfile.objects.get(id=wholesaler_id)
        except WholesalerProfile.DoesNotExist:
            return Response({"error": "Wholesaler not found."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id, wholesaler=wholesaler)
        except Product.DoesNotExist:
            return Response({"error": "Product not found under selected wholesaler."}, status=status.HTTP_400_BAD_REQUEST)

        stock = product.stocks.order_by("-created_at").first()
        if stock is None:
            return Response({"error": "This product currently has no stock."}, status=status.HTTP_400_BAD_REQUEST)

        price_per_unit = stock.selling_price
        total_price = quantity * price_per_unit

        with transaction.atomic():
            order = Order.objects.create(
                retailer=retailer,
                wholesaler=wholesaler,
                status="PENDING",
                notes=notes
            )
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price_per_unit=price_per_unit,
                total_price=total_price
            )

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def order_detail_api(request, order_id):
    profile = getattr(request.user, "profile", None)

    if profile is None:
        raise PermissionDenied("User profile is not configured.")

    try:
        if profile.role == "WHOLESALER":
            order = Order.objects.get(id=order_id, wholesaler__user=request.user)
        elif profile.role == "RETAILER":
            order = Order.objects.get(id=order_id, retailer__user=request.user)
        else:
            raise PermissionDenied("You cannot access orders.")
    except Order.DoesNotExist:
        raise NotFound("Order not found.")

    if request.method == "GET":
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    elif request.method == "PATCH":
        if profile.role != "WHOLESALER":
            raise PermissionDenied("Only wholesalers can update order status.")

        action = request.data.get("action")
        if order.status != "PENDING":
            return Response({"error": f"Cannot change status for order currently in '{order.status}' status."}, status=status.HTTP_400_BAD_REQUEST)

        if action == "accept":
            order.status = "ACCEPTED"
            order.save(update_fields=["status"])
            fulfilled = fulfill_order(order.id)
            if not fulfilled:
                order.status = "WAITING_FOR_STOCK"
                order.save(update_fields=["status"])

        elif action == "reject":
            order.status = "REJECTED"
            order.save(update_fields=["status"])
        else:
            return Response({"error": "Invalid action. Use 'accept' or 'reject'."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = OrderSerializer(order)
        return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def fulfill_waiting_order_api(request, order_id):
    profile = getattr(request.user, "profile", None)

    if profile is None or profile.role != "WHOLESALER":
        raise PermissionDenied("Only wholesalers can fulfill waiting orders.")

    try:
        order = Order.objects.get(id=order_id, wholesaler__user=request.user)
    except Order.DoesNotExist:
        raise NotFound("Order not found.")

    if order.status != "WAITING_FOR_STOCK":
        return Response({"error": f"Order status is '{order.status}', not 'WAITING_FOR_STOCK'."}, status=status.HTTP_400_BAD_REQUEST)

    fulfilled = fulfill_order(order.id)
    if not fulfilled:
        return Response({"message": "Stock is still insufficient to fulfill order.", "status": order.status}, status=status.HTTP_400_BAD_REQUEST)

    order.refresh_from_db()
    serializer = OrderSerializer(order)
    return Response({"message": "Order fulfilled successfully.", "order": serializer.data})
