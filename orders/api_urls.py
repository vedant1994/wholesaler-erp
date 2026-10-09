from django.urls import path
from .api_views import order_list_create_api, order_detail_api, fulfill_waiting_order_api

urlpatterns = [
    path("", order_list_create_api, name="api_order_list_create"),
    path("<int:order_id>/", order_detail_api, name="api_order_detail"),
    path("<int:order_id>/fulfill/", fulfill_waiting_order_api, name="api_fulfill_waiting_order"),
]
