from django.urls import path
from .api_views import shipment_list_create_api, shipment_detail_api

urlpatterns = [
    path("", shipment_list_create_api, name="api_shipment_list_create"),
    path("<int:shipment_id>/", shipment_detail_api, name="api_shipment_detail"),
]
