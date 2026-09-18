from django.urls import path
from .views import wholesaler_list, wholesaler_products

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
]