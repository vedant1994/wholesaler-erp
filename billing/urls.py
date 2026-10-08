from django.urls import include, path

from . import views

urlpatterns = [
    path(
        "invoice/genrate/<int:order_id>/",
        views.genrate_invoice_view,
        name="genrate_invoice"
    ),

    path(
        "invoice/<int:invoice_id>/",
        views.invoice_detail,
        name="invoice_detail"
    ),

    path(
        "<int:invoice_id>/",
        views.invoice_detail
    ),


    path(
        "invoices/",
        views.invoice_list,
        name="invoice_list"
    ),

    path(
        "invoice/<int:invoice_id>/pdf/",
        views.invoice_pdf,
        name="invoice_pdf"
    ),
    path(
        "customer-invoices/",
        views.customer_invoices_view,
        name="customer_invoices"
    ),
]