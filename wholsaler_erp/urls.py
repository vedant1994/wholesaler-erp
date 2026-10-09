"""
URL configuration for wholsaler_erp project.
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse
from accounts.views import reports_view


def home(request):
    return render(request, 'home.html')


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request, format=None):
    """
    Wholesaler ERP REST API Root Endpoint for Browser & Client Navigation
    """
    return Response({
        "accounts": {
            "register": reverse("api_register", request=request, format=format),
            "login": reverse("api_login", request=request, format=format),
            "logout": reverse("api_logout", request=request, format=format),
            "profile": reverse("api_user_profile", request=request, format=format),
            "dashboard_stats": reverse("api_dashboard_stats", request=request, format=format),
            "retailers": reverse("api_retailer_list", request=request, format=format),
            "notifications": reverse("api_notification_list", request=request, format=format),
        },
        "products": {
            "products": reverse("api_product_list_create", request=request, format=format),
            "stock": reverse("api_stock_list_create", request=request, format=format),
            "retailer_stock": reverse("api_retailer_stock_list", request=request, format=format),
        },
        "orders": {
            "orders": reverse("api_order_list_create", request=request, format=format),
        },
        "billing": {
            "invoices": reverse("api_invoice_list", request=request, format=format),
            "customer_invoices": reverse("api_customer_invoice_list_create", request=request, format=format),
        },
        "payments": {
            "payments": reverse("api_payment_list_create", request=request, format=format),
            "ledger": reverse("api_ledger_list", request=request, format=format),
            "customer_payments": reverse("api_customer_payment_list", request=request, format=format),
        },
        "customers": {
            "customers": reverse("api_customer_list_create", request=request, format=format),
        },
        "shipping": {
            "shipments": reverse("api_shipment_list_create", request=request, format=format),
        },
    })


urlpatterns = [
    # Admin Panel
    path('admin/', admin.site.urls),

    # Web HTML Views (Preserved 100%)
    path('', home, name='home'),
    path('reports/', reports_view, name='reports'),
    path('accounts/', include("accounts.urls")),
    path('products/', include("products.urls")),
    path('orders/', include("orders.urls")),
    path('billing/', include("billing.urls")),
    path('payments/', include("payments.urls")),
    path('coustomers/', include("coustomers.urls")),
    path('shipping/', include("shipping.urls")),

    # Browser DRF Auth URLs (Login/Logout button in browser API pages)
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # REST API Root & App Endpoints
    path('api/', api_root, name='api_root'),
    path('api/accounts/', include("accounts.api_urls")),
    path('api/products/', include("products.api_urls")),
    path('api/orders/', include("orders.api_urls")),
    path('api/billing/', include("billing.api_urls")),
    path('api/payments/', include("payments.api_urls")),
    path('api/customers/', include("coustomers.api_urls")),
    path('api/shipping/', include("shipping.api_urls")),
]
