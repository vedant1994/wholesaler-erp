from datetime import date, timedelta
from django.db.models import F, Q
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Product, Stock, RetailerStock
from .serializers import ProductSerializer, StockSerializer, RetailerStockSerializer


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def product_list_create_api(request):
    profile = getattr(request.user, "profile", None)

    if profile is None:
        raise PermissionDenied("User profile is not configured.")

    if request.method == "GET":
        if profile.role == "WHOLESALER":
            products = Product.objects.filter(wholesaler__user=request.user)
        elif profile.role == "RETAILER":
            products = Product.objects.filter(wholesaler__retailers__user=request.user).distinct()
        else:
            raise PermissionDenied("You cannot access products.")

        category = request.GET.get("category", "")
        if category:
            products = products.filter(category=category)

        search = request.GET.get("search", "")
        if search:
            products = products.filter(Q(name__icontains=search) | Q(sku__icontains=search))

        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        if profile.role != "WHOLESALER":
            raise PermissionDenied("Only wholesalers can add products.")

        wholesaler = getattr(request.user, "wholesaler_profile", None)
        if not wholesaler:
            raise PermissionDenied("Wholesaler profile is missing.")

        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(wholesaler=wholesaler)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def product_detail_api(request, product_id):
    profile = getattr(request.user, "profile", None)

    if profile is None:
        raise PermissionDenied("User profile is not configured.")

    try:
        if profile.role == "WHOLESALER":
            product = Product.objects.get(id=product_id, wholesaler__user=request.user)
        elif profile.role == "RETAILER":
            product = Product.objects.get(id=product_id, wholesaler__retailers__user=request.user)
        else:
            raise PermissionDenied("You cannot access this product.")
    except Product.DoesNotExist:
        raise NotFound("Product not found.")

    if request.method == "GET":
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    elif request.method in ["PUT", "PATCH"]:
        if profile.role != "WHOLESALER":
            raise PermissionDenied("Only wholesalers can update products.")

        partial = (request.method == "PATCH")
        serializer = ProductSerializer(product, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        if profile.role != "WHOLESALER":
            raise PermissionDenied("Only wholesalers can delete products.")

        product.delete()
        return Response({"message": "Product deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def stock_list_create_api(request):
    profile = getattr(request.user, "profile", None)

    if profile is None:
        raise PermissionDenied("User profile is not configured.")

    if request.method == "GET":
        if profile.role == "WHOLESALER":
            stocks = Stock.objects.filter(product__wholesaler__user=request.user).select_related("product")
        elif profile.role == "RETAILER":
            stocks = Stock.objects.filter(product__wholesaler__retailers__user=request.user).select_related("product")
        else:
            raise PermissionDenied("You cannot access stock data.")

        search = request.GET.get("search", "")
        if search:
            stocks = stocks.filter(Q(product__name__icontains=search) | Q(product__sku__icontains=search))

        category = request.GET.get("category", "")
        if category:
            stocks = stocks.filter(product__category=category)

        stock_status = request.GET.get("stock_status", "")
        if stock_status == "low":
            stocks = stocks.filter(quantity__lte=F("minimum_stock"))
        elif stock_status == "in_stock":
            stocks = stocks.filter(quantity__gt=F("minimum_stock"))

        today = date.today()
        expiry_limit = today + timedelta(days=30)

        expiry_status = request.GET.get("expiry_status", "")
        if expiry_status == "expired":
            stocks = stocks.filter(expiry_date__lt=today)
        elif expiry_status == "soon_expiring":
            stocks = stocks.filter(expiry_date__gte=today, expiry_date__lte=expiry_limit)
        elif expiry_status == "good":
            stocks = stocks.filter(expiry_date__gt=expiry_limit)

        serializer = StockSerializer(stocks, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        if profile.role != "WHOLESALER":
            raise PermissionDenied("Only wholesalers can add stock.")

        wholesaler = getattr(request.user, "wholesaler_profile", None)
        product_id = request.data.get("product")
        try:
            product = Product.objects.get(id=product_id, wholesaler=wholesaler)
        except Product.DoesNotExist:
            return Response({"error": "Selected product does not belong to your wholesaler account."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = StockSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def stock_detail_api(request, stock_id):
    profile = getattr(request.user, "profile", None)

    if profile is None:
        raise PermissionDenied("User profile is not configured.")

    try:
        if profile.role == "WHOLESALER":
            stock = Stock.objects.get(id=stock_id, product__wholesaler__user=request.user)
        elif profile.role == "RETAILER":
            stock = Stock.objects.get(id=stock_id, product__wholesaler__retailers__user=request.user)
        else:
            raise PermissionDenied("You cannot access stock data.")
    except Stock.DoesNotExist:
        raise NotFound("Stock entry not found.")

    if request.method == "GET":
        serializer = StockSerializer(stock)
        return Response(serializer.data)

    elif request.method in ["PUT", "PATCH"]:
        if profile.role != "WHOLESALER":
            raise PermissionDenied("Only wholesalers can update stock.")

        partial = (request.method == "PATCH")
        serializer = StockSerializer(stock, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        if profile.role != "WHOLESALER":
            raise PermissionDenied("Only wholesalers can delete stock.")

        stock.delete()
        return Response({"message": "Stock entry deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def retailer_stock_list_api(request):
    profile = getattr(request.user, "profile", None)

    if profile is None or profile.role != "RETAILER":
        raise PermissionDenied("Only retailers can view retailer stock.")

    stocks = RetailerStock.objects.filter(retailer__user=request.user)
    serializer = RetailerStockSerializer(stocks, many=True)
    return Response(serializer.data)