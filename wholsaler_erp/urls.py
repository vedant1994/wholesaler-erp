"""
URL configuration for wholsaler_erp project.
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from accounts.views import reports_view

def home(request):
    return render(request, 'home.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('reports/', reports_view, name='reports'),
    path('accounts/', include("accounts.urls")),
    path('products/', include("products.urls")),
    path('orders/', include("orders.urls")),
    path('billing/', include("billing.urls")),
    path('payments/', include("payments.urls")),
    path('coustomers/', include("coustomers.urls")),
    path('shipping/', include("shipping.urls")),
]
