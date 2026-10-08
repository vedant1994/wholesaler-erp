from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.db import models
from django.contrib import messages
from django.http import FileResponse
from .pdf import generate_invoice_pdf

from orders.models import Order
from .models import Invoice
from .services import generate_invoice

# Create your views here.

@login_required
def genrate_invoice_view(request, order_id):

    wholesaler = request.user.wholesaler_profile

    order = get_object_or_404(
        Order,
        id=order_id,
        wholesaler=wholesaler
    )

    if request.method != "POST":
        return redirect(
            "wholeslaer_order_detail",
            order_id = order.id
        )

    try:
        invoice = generate_invoice(order.id)

    except ValidationError as e:
        messages.error(request, str(e))
        return redirect(
            "wholesaler_order_detail",
            order_id = order.id
        )

    messages.success(
        request,
        f"Invoice {invoice.invoice_number} generated successfully."
    )

    return redirect(
        "invoice_detail",
        invoice_id=invoice.id
    )

@login_required
def invoice_detail(request, invoice_id):
    wholesaler = request.user.wholesaler_profile

    invoice = get_object_or_404(
        Invoice.objects
        .select_related(
            "order",
            "wholesaler",
            "retailer",
        )
        .prefetch_related(
            "items__product"
        ),
        id=invoice_id,
        wholesaler = wholesaler
    )

    return render(
        request,
        "billing/invoice_detail.html",
        {
            "invoice": invoice
        }
    )

@login_required
def invoice_list(request):
    wholesaler = request.user.wholesaler_profile

    invoices = (
        Invoice.objects
        .filter(wholesaler=wholesaler)
        .select_related(
            "retailer",
            "order",
        )
        .order_by("-invoice_date")
    )

    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "").strip()

    if search:
        invoice = invoices.filter(
            models.Q(invoice_number__icontains=search)
            | models.Q(retailer__shop_name__icontains=search)
        )

    if status:
        invoices = invoices.filter(status=status)

    context = {
        "invoices": invoices,
        "search": search,
        "status": status,
        "status_choices": Invoice.STATUS_CHOICES,
    }

    return render(
        request,
        "billing/invoice_list.html",
        context
    )

@login_required
def invoice_pdf(request, invoice_id):

    wholesaler = request.user.wholesaler_profile

    pdf_buffer = generate_invoice_pdf(
        invoice_id,
        wholesaler
    )

    return FileResponse(
        pdf_buffer,
        as_attachment=True,
        filename=f"invoice-{invoice_id}.pdf",
        content_type="application/pdf"
    )