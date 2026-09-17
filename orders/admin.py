from django.contrib import admin
from .models import Order, OrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "retailer",
        "wholesaler",
        "status",
        "order_date",
    )

    list_filter = (
        "status",
        "order_date",
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        "order",
        "product",
        "quantity",
        "price_per_unit",
        "total_price",
    )