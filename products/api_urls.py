from django.urls import path
from .api_views import (
    product_list_create_api,
    product_detail_api,
    stock_list_create_api,
    stock_detail_api,
    retailer_stock_list_api,
)

urlpatterns = [
    path("", product_list_create_api, name="api_product_list_create"),
    path("<int:product_id>/", product_detail_api, name="api_product_detail"),
    path("stock/", stock_list_create_api, name="api_stock_list_create"),
    path("stock/<int:stock_id>/", stock_detail_api, name="api_stock_detail"),
    path("retailer-stock/", retailer_stock_list_api, name="api_retailer_stock_list"),
]
