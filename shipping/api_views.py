from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from orders.models import Order
from .models import Shipment
from .serializers import ShipmentSerializer


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def shipment_list_create_api(request):
    profile = getattr(request.user, "profile", None)

    if profile is None:
        raise PermissionDenied("User profile is not configured.")

    if request.method == "GET":
        if profile.role == "WHOLESALER":
            shipments = Shipment.objects.filter(order__wholesaler__user=request.user).order_by("-created_at")
        elif profile.role == "RETAILER":
            shipments = Shipment.objects.filter(order__retailer__user=request.user).order_by("-created_at")
        else:
            raise PermissionDenied("You cannot access shipments.")

        serializer = ShipmentSerializer(shipments, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        if profile.role != "WHOLESALER":
            raise PermissionDenied("Only wholesalers can create shipments.")

        order_id = request.data.get("order")
        try:
            Order.objects.get(id=order_id, wholesaler__user=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found under your wholesaler account."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ShipmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def shipment_detail_api(request, shipment_id):
    profile = getattr(request.user, "profile", None)

    if profile is None:
        raise PermissionDenied("User profile is not configured.")

    try:
        if profile.role == "WHOLESALER":
            shipment = Shipment.objects.get(id=shipment_id, order__wholesaler__user=request.user)
        elif profile.role == "RETAILER":
            shipment = Shipment.objects.get(id=shipment_id, order__retailer__user=request.user)
        else:
            raise PermissionDenied("You cannot access shipments.")
    except Shipment.DoesNotExist:
        raise NotFound("Shipment not found.")

    if request.method == "GET":
        serializer = ShipmentSerializer(shipment)
        return Response(serializer.data)

    elif request.method in ["PUT", "PATCH"]:
        if profile.role != "WHOLESALER":
            raise PermissionDenied("Only wholesalers can update shipments.")

        partial = (request.method == "PATCH")
        serializer = ShipmentSerializer(shipment, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
