from django.urls import path

from . import views

urlpatterns = [
    path(
        "invoice/<int:invoice_id>/pay/",
        views.create_invoice_payment,
        name="create_invoice_payment"
    ),
]