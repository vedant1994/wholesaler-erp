from django.urls import path
from .views import wholesaler_list, wholesaler_products, create_order, my_orders, order_detail, wholesaler_orders, wholesaler_order_detail

urlpatterns = [
    path(
        "wholesalers/",
        wholesaler_list,
        name="wholesaler_list"
    ),

    path(
        "wholesalers/<int:wholesaler_id>/products/",
        wholesaler_products,
        name="wholesaler_products"
    ),

    path(
        "wholesaler/<int:wholesaler_id>/products/<int:product_id>/order/",
        create_order,
        name="create_order"
    ),

    path(
        "my-orders/",
        my_orders,
        name="my_orders"
    ),

    path(
        "my-orders/<int:order_id>/",
        order_detail,
        name="order_detail"
    ),

    path(
        "wholesaler/orders/",
        wholesaler_orders,
        name="wholesaler_orders"
    ),

    path(
        "wholesaler/orders/<int:order_id>/",
        wholesaler_order_detail,
        name="wholesaler_order_detail"
    ),


]