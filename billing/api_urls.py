from django.urls import path
from .api_views import (
    invoice_list_api,
    generate_invoice_api,
    invoice_detail_api,
    invoice_pdf_api,
    customer_invoice_list_create_api,
    customer_invoice_detail_api,
)

urlpatterns = [
    path("invoices/", invoice_list_api, name="api_invoice_list"),
    path("invoices/generate/<int:order_id>/", generate_invoice_api, name="api_generate_invoice"),
    path("invoices/<int:invoice_id>/", invoice_detail_api, name="api_invoice_detail"),
    path("invoices/<int:invoice_id>/pdf/", invoice_pdf_api, name="api_invoice_pdf"),
    path("customer-invoices/", customer_invoice_list_create_api, name="api_customer_invoice_list_create"),
    path("customer-invoices/<int:invoice_id>/", customer_invoice_detail_api, name="api_customer_invoice_detail"),
]
