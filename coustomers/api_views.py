from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Customer
from .serializers import CustomerSerializer


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def customer_list_create_api(request):
    profile = getattr(request.user, "profile", None)

    if profile is None or profile.role != "RETAILER":
        raise PermissionDenied("Only retailers can manage customers.")

    retailer = getattr(request.user, "retailer_profile", None)

    if request.method == "GET":
        customers = Customer.objects.filter(retailer=retailer).order_by("-created_at")
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(retailer=retailer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def customer_detail_api(request, customer_id):
    profile = getattr(request.user, "profile", None)

    if profile is None or profile.role != "RETAILER":
        raise PermissionDenied("Only retailers can manage customers.")

    try:
        customer = Customer.objects.get(id=customer_id, retailer__user=request.user)
    except Customer.DoesNotExist:
        raise NotFound("Customer not found.")

    if request.method == "GET":
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)

    elif request.method in ["PUT", "PATCH"]:
        partial = (request.method == "PATCH")
        serializer = CustomerSerializer(customer, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        customer.delete()
        return Response({"message": "Customer deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
