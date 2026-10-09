from django.urls import path
from .api_views import customer_list_create_api, customer_detail_api

urlpatterns = [
    path("", customer_list_create_api, name="api_customer_list_create"),
    path("<int:customer_id>/", customer_detail_api, name="api_customer_detail"),
]
