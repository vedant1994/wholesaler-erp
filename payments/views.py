from django.shortcuts import render

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from .models import Payment, LedgerEntry, CustomerPayment
from decimal import Decimal 

from billing.models import Invoice

from .forms import PaymentForm
from .services import create_payment

# Create your views here.

@login_required
def create_invoice_payment(request, invoice_id):

    wholesaler = request.user.wholesaler_profile

    invoice = get_object_or_404(
        Invoice,
        id = invoice_id,
        wholesaler = wholesaler
    )

    if invoice.status == "CANCELLED":
        messages.error(
            request,
            "Payments cannot be added to a cancelled invoice."
        )

        return redirect(
            "invoice_detail",
            invoice_id = invoice.id
        )

    if request.method == "POST":

        form = PaymentForm(request.POST)

        if form.is_valid():

            try:

                payment = create_payment(
                    invoice_id=invoice.id,
                    amount=form.cleaned_data[
                        "amount"
                    ],
                    payment_method=form.cleaned_data["payment_method"],
                    reference_number=form.cleaned_data[
                        "reference_number"
                    ],
                    notes=form.cleaned_data["notes"],
                )

            except ValidationError as e:

                form.add_error(
                    None,
                    str(e)
                )

            else:

                messages.success(
                    request,
                    f"Payment of ₹{payment.amount} recorded successfully."
                )

                return redirect(
                    "invoice_detail",
                    invoice_id = invoice.id
                )

    else:

        form = PaymentForm()

    total_paid = sum(
        (
            payment.amount
            for payment in invoice.payments.all()
        ),
        Decimal("0.00")
        )

    outstanding = invoice.grand_total - total_paid

    return render(
        request,
        "payments/create_payment.html",
        {
            "invoice": invoice,
            "form": form,
            "total_paid": total_paid,
            "outstanding": outstanding,
        }
    )


@login_required
def payment_list(request):
    profile = getattr(request.user, 'profile', None)
    if profile and profile.role == "WHOLESALER":
        wholesaler = request.user.wholesaler_profile
        payments = Payment.objects.filter(invoice__wholesaler=wholesaler).select_related("invoice", "invoice__retailer").order_by("-created_at")
    elif profile and profile.role == "RETAILER":
        retailer = request.user.retailer_profile
        payments = Payment.objects.filter(invoice__retailer=retailer).select_related("invoice", "invoice__wholesaler").order_by("-created_at")
    else:
        payments = Payment.objects.none()

    return render(request, "payments/payment_list.html", {"payments": payments})

@login_required
def ledger_view(request):
    profile = getattr(request.user, 'profile', None)
    if profile and profile.role == "WHOLESALER":
        wholesaler = request.user.wholesaler_profile
        entries = LedgerEntry.objects.filter(wholesaler=wholesaler).select_related("retailer", "invoice", "payment").order_by("-created_at")
    elif profile and profile.role == "RETAILER":
        retailer = request.user.retailer_profile
        entries = LedgerEntry.objects.filter(retailer=retailer).select_related("wholesaler", "invoice", "payment").order_by("-created_at")
    else:
        entries = LedgerEntry.objects.none()

    return render(request, "payments/ledger_list.html", {"entries": entries})

@login_required
def customer_payment_view(request):
    profile = getattr(request.user, 'profile', None)
    if profile and profile.role == "RETAILER":
        retailer = request.user.retailer_profile
        payments = CustomerPayment.objects.filter(invoice__retailer=retailer).select_related("invoice", "invoice__customer").order_by("-created_at")
    else:
        payments = CustomerPayment.objects.none()

    return render(request, "payments/customer_payment_list.html", {"payments": payments})

