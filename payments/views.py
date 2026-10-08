from django.shortcuts import render

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
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
