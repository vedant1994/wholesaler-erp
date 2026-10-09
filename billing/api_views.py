from decimal import Decimal
import uuid
from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.http import FileResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from orders.models import Order
from .models import Invoice, CustomerInvoice, CustomerInvoiceItem
from .serializers import InvoiceSerializer, CustomerInvoiceSerializer
from .services import generate_invoice
from .pdf import generate_invoice_pdf


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def invoice_list_api(request):
    profile = getattr(request.user, "profile", None)

    if profile is None:
        raise PermissionDenied("User profile is not configured.")

    if profile.role == "WHOLESALER":
        invoices = Invoice.objects.filter(wholesaler__user=request.user)
    elif profile.role == "RETAILER":
        invoices = Invoice.objects.filter(retailer__user=request.user)
    else:
        raise PermissionDenied("You cannot access invoices.")

    search = request.GET.get("search", "").strip()
    status_param = request.GET.get("status", "").strip()

    if search:
        invoices = invoices.filter(
            models.Q(invoice_number__icontains=search)
            | models.Q(retailer__shop_name__icontains=search)
            | models.Q(wholesaler__business_name__icontains=search)
        )

    if status_param:
        invoices = invoices.filter(status=status_param)

    invoices = invoices.select_related("wholesaler", "retailer", "order").prefetch_related("payments").order_by("-invoice_date")
    serializer = InvoiceSerializer(invoices, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generate_invoice_api(request, order_id):
    profile = getattr(request.user, "profile", None)

    if profile is None or profile.role != "WHOLESALER":
        raise PermissionDenied("Only wholesalers can generate invoices.")

    wholesaler = getattr(request.user, "wholesaler_profile", None)
    try:
        order = Order.objects.get(id=order_id, wholesaler=wholesaler)
    except Order.DoesNotExist:
        raise NotFound("Order not found under your wholesaler account.")

    try:
        invoice = generate_invoice(order.id)
    except ValidationError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    serializer = InvoiceSerializer(invoice)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def invoice_detail_api(request, invoice_id):
    profile = getattr(request.user, "profile", None)

    if profile is None:
        raise PermissionDenied("User profile is not configured.")

    try:
        if profile.role == "WHOLESALER":
            invoice = Invoice.objects.get(id=invoice_id, wholesaler__user=request.user)
        elif profile.role == "RETAILER":
            invoice = Invoice.objects.get(id=invoice_id, retailer__user=request.user)
        else:
            raise PermissionDenied("You cannot access invoices.")
    except Invoice.DoesNotExist:
        raise NotFound("Invoice not found.")

    serializer = InvoiceSerializer(invoice)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def invoice_pdf_api(request, invoice_id):
    profile = getattr(request.user, "profile", None)

    if profile is None or profile.role != "WHOLESALER":
        raise PermissionDenied("Only wholesalers can download invoice PDFs.")

    wholesaler = getattr(request.user, "wholesaler_profile", None)
    try:
        Invoice.objects.get(id=invoice_id, wholesaler=wholesaler)
    except Invoice.DoesNotExist:
        raise NotFound("Invoice not found.")

    pdf_buffer = generate_invoice_pdf(invoice_id, wholesaler)
    return FileResponse(
        pdf_buffer,
        as_attachment=True,
        filename=f"invoice-{invoice_id}.pdf",
        content_type="application/pdf"
    )


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def customer_invoice_list_create_api(request):
    profile = getattr(request.user, "profile", None)

    if profile is None or profile.role != "RETAILER":
        raise PermissionDenied("Only retailers can manage customer invoices.")

    retailer = getattr(request.user, "retailer_profile", None)

    if request.method == "GET":
        invoices = CustomerInvoice.objects.filter(retailer=retailer).order_by("-created_at")
        serializer = CustomerInvoiceSerializer(invoices, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        customer_name = request.data.get("customer_name")
        if not customer_name:
            return Response({"error": "customer_name is required."}, status=status.HTTP_400_BAD_REQUEST)

        customer_phone = request.data.get("customer_phone", "")
        billing_address = request.data.get("billing_address", "")
        shipping_address = request.data.get("shipping_address", "") or billing_address
        payment_method = request.data.get("payment_method", "CASH")
        payment_due = request.data.get("payment_due", "On Receipt")
        upi_details = request.data.get("upi_details", "abc@upi")
        items_input = request.data.get("items", [])

        if not items_input or not isinstance(items_input, list):
            return Response({"error": "items must be a non-empty list."}, status=status.HTTP_400_BAD_REQUEST)

        subtotal = Decimal("0.00")
        total_discount = Decimal("0.00")
        items_data = []

        for item_dict in items_input:
            p_name = item_dict.get("product_name", "").strip()
            if not p_name:
                continue
            qty = Decimal(str(item_dict.get("quantity", 1)))
            price = Decimal(str(item_dict.get("unit_price", 0)))
            disc = Decimal(str(item_dict.get("discount", 0)))
            hsn = item_dict.get("hsn_code", "6109")

            line_sub = qty * price
            line_amount = line_sub - disc

            subtotal += line_sub
            total_discount += disc

            items_data.append({
                "product_name": p_name,
                "hsn_code": hsn,
                "quantity": qty,
                "unit_price": price,
                "discount": disc,
                "amount": line_amount,
            })

        if not items_data:
            return Response({"error": "No valid items provided."}, status=status.HTTP_400_BAD_REQUEST)

        net_taxable = subtotal - total_discount
        cgst_amount = (net_taxable * Decimal("0.09")).quantize(Decimal("0.01")) if net_taxable > 0 else Decimal("0.00")
        sgst_amount = (net_taxable * Decimal("0.09")).quantize(Decimal("0.01")) if net_taxable > 0 else Decimal("0.00")

        raw_grand = net_taxable + cgst_amount + sgst_amount
        grand_total = raw_grand.quantize(Decimal("1."), rounding="ROUND_HALF_UP")
        round_off = grand_total - raw_grand

        inv_num = f"INV-{uuid.uuid4().hex[:6].upper()}"

        with transaction.atomic():
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

        serializer = CustomerInvoiceSerializer(invoice)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def customer_invoice_detail_api(request, invoice_id):
    profile = getattr(request.user, "profile", None)

    if profile is None or profile.role != "RETAILER":
        raise PermissionDenied("Only retailers can access customer invoices.")

    try:
        invoice = CustomerInvoice.objects.get(id=invoice_id, retailer__user=request.user)
    except CustomerInvoice.DoesNotExist:
        raise NotFound("Customer invoice not found.")

    serializer = CustomerInvoiceSerializer(invoice)
    return Response(serializer.data)
