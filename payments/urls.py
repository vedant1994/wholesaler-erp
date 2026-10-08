from django.urls import path
from . import views

urlpatterns = [
    path("", views.payment_list, name="payment_list"),
    path("ledger/", views.ledger_view, name="payment_ledger"),
    path("customer/", views.customer_payment_view, name="customer_payments"),
    path(
        "invoice/<int:invoice_id>/pay/",
        views.create_invoice_payment,
        name="create_invoice_payment"
    ),
]