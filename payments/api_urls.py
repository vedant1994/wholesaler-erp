from django.urls import path
from .api_views import payment_list_create_api, ledger_list_api, customer_payment_list_api

urlpatterns = [
    path("", payment_list_create_api, name="api_payment_list_create"),
    path("ledger/", ledger_list_api, name="api_ledger_list"),
    path("customer-payments/", customer_payment_list_api, name="api_customer_payment_list"),
]
