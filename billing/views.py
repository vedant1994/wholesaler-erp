from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.db import models
from django.contrib import messages
from django.http import FileResponse
from .pdf import generate_invoice_pdf
from decimal import Decimal

from orders.models import Order
from .models import Invoice, Product
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
            "wholesaler_order_detail",
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
    profile = getattr(request.user, 'profile', None)
    if profile and profile.role == "WHOLESALER":
        wholesaler = request.user.wholesaler_profile
        invoice = get_object_or_404(
            Invoice.objects.select_related("order", "wholesaler", "retailer").prefetch_related("items__product", "payments"),
            id=invoice_id,
            wholesaler=wholesaler
        )
    elif profile and profile.role == "RETAILER":
        retailer = request.user.retailer_profile
        invoice = get_object_or_404(
            Invoice.objects.select_related("order", "wholesaler", "retailer").prefetch_related("items__product", "payments"),
            id=invoice_id,
            retailer=retailer
        )
    else:
        invoice = get_object_or_404(
            Invoice.objects.select_related("order", "wholesaler", "retailer").prefetch_related("items__product", "payments"),
            id=invoice_id
        )

    total_paid = sum(p.amount for p in invoice.payments.all())
    outstanding = max(0, invoice.grand_total - total_paid)

    full_invoice_url = request.build_absolute_uri(reverse("invoice_detail", kwargs={"invoice_id": invoice.id}))
    qr_code_image = generate_qr_code(full_invoice_url)

    return render(
        request,
        "billing/invoice_detail.html",
        {
            "invoice": invoice,
            "total_paid": total_paid,
            "outstanding": outstanding,
            "qr_code_image": qr_code_image,
        }
    )


@login_required
def invoice_list(request):
    profile = getattr(request.user, 'profile', None)
    if profile and profile.role == "WHOLESALER":
        wholesaler = request.user.wholesaler_profile
        invoices = (
            Invoice.objects
            .filter(wholesaler=wholesaler)
            .select_related("retailer", "order")
            .order_by("-invoice_date")
        )
    elif profile and profile.role == "RETAILER":
        retailer = request.user.retailer_profile
        invoices = (
            Invoice.objects
            .filter(retailer=retailer)
            .select_related("wholesaler", "order")
            .order_by("-invoice_date")
        )
    else:
        invoices = Invoice.objects.none()

    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "").strip()

    if search:
        invoices = invoices.filter(
            models.Q(invoice_number__icontains=search)
            | models.Q(retailer__shop_name__icontains=search)
            | models.Q(wholesaler__business_name__icontains=search)
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

from .models import CustomerInvoice, CustomerInvoiceItem
from products.models import Product, Stock, RetailerStock
import uuid
import json

@login_required
def customer_invoices_view(request):
    profile = getattr(request.user, 'profile', None)
    if profile and profile.role == "RETAILER":
        retailer = request.user.retailer_profile
        invoices = CustomerInvoice.objects.filter(retailer=retailer).order_by("-invoice_date")
    else:
        invoices = CustomerInvoice.objects.none()

    return render(request, "billing/customer_invoice_list.html", {"invoices": invoices})

@login_required
def create_customer_invoice(request):
    retailer = request.user.retailer_profile
    
    # Auto-detect product catalog with prices
    products_qs = Product.objects.prefetch_related('stocks').all()
    products_list = []
    for p in products_qs:
        st = p.stocks.first()
        price = float(st.selling_price) if (st and st.selling_price) else 0.00
        products_list.append({
            "id": p.id,
            "name": p.name,
            "hsn": p.sku or "6109",
            "price": price,
            "gst": float(p.gst_rate) if p.gst_rate else 5.0
        })

    products_json = json.dumps(products_list)

    if request.method == "POST":
        customer_name = request.POST.get("customer_name")
        customer_phone = request.POST.get("customer_phone", "")
        billing_address = request.POST.get("billing_address", "")
        shipping_address = request.POST.get("shipping_address", "") or billing_address
        payment_method = request.POST.get("payment_method", "CASH")
        payment_due = request.POST.get("payment_due", "On Receipt")
        upi_details = request.POST.get("upi_details", "abc@upi")
        
        product_names = request.POST.getlist("product_name")
        hsn_codes = request.POST.getlist("hsn_code")
        quantities = request.POST.getlist("quantity")
        unit_prices = request.POST.getlist("unit_price")
        discounts = request.POST.getlist("discount")

        subtotal = Decimal("0.00")
        total_discount = Decimal("0.00")
        items_data = []

        for i in range(len(product_names)):
            if not product_names[i].strip():
                continue
            qty = Decimal(quantities[i] or "1")
            price = Decimal(unit_prices[i] or "0")
            disc = Decimal(discounts[i] or "0")
            
            line_sub = qty * price
            line_amount = line_sub - disc
            
            subtotal += line_sub
            total_discount += disc

            items_data.append({
                "product_name": product_names[i],
                "hsn_code": hsn_codes[i] or "6109",
                "quantity": qty,
                "unit_price": price,
                "discount": disc,
                "amount": line_amount,
            })

        net_taxable = subtotal - total_discount
        cgst_amount = (net_taxable * Decimal("0.09")).quantize(Decimal("0.01")) if net_taxable > 0 else Decimal("0.00")
        sgst_amount = (net_taxable * Decimal("0.09")).quantize(Decimal("0.01")) if net_taxable > 0 else Decimal("0.00")
        
        raw_grand = net_taxable + cgst_amount + sgst_amount
        grand_total = raw_grand.quantize(Decimal("1."), rounding="ROUND_HALF_UP")
        round_off = grand_total - raw_grand

        inv_num = f"INV-{uuid.uuid4().hex[:6].upper()}"

        invoice = CustomerInvoice.objects.create(
            invoice_number=inv_num,
            retailer=retailer,
            customer_name=customer_name,
            customer_phone=customer_phone,
            billing_address=billing_address,
            shipping_address=shipping_address,
            payment_due=payment_due,
            subtotal=subtotal,
            total_discount=total_discount,
            cgst_amount=cgst_amount,
            sgst_amount=sgst_amount,
            round_off=round_off,
            grand_total=grand_total,
            payment_method=payment_method,
            amount_paid=grand_total,
            balance_due=Decimal("0.00"),
            upi_details=upi_details,
            status="PAID"
        )

        for item in items_data:
            CustomerInvoiceItem.objects.create(
                invoice=invoice,
                product_name=item["product_name"],
                hsn_code=item["hsn_code"],
                quantity=item["quantity"],
                unit_price=item["unit_price"],
                discount=item["discount"],
                amount=item["amount"],
            )

        return redirect("customer_invoice_detail", invoice_id=invoice.id)

    return render(request, "billing/create_customer_invoice.html", {
        "products_json": products_json,
        "products": products_list,
        "retailer": retailer
    })

import qrcode
import io
import base64
from django.urls import reverse

def generate_qr_code(text_data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=4,
        border=2,
    )
    qr.add_data(text_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    b64_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64_str}"

@login_required
def customer_invoice_detail(request, invoice_id):
    retailer = request.user.retailer_profile
    invoice = get_object_or_404(CustomerInvoice.objects.prefetch_related("items"), id=invoice_id, retailer=retailer)
    
    full_invoice_url = request.build_absolute_uri(reverse("customer_invoice_detail", kwargs={"invoice_id": invoice.id}))
    qr_code_image = generate_qr_code(full_invoice_url)

    return render(request, "billing/customer_invoice_detail.html", {
        "invoice": invoice,
        "retailer": retailer,
        "qr_code_image": qr_code_image,
        "full_invoice_url": full_invoice_url
    })

