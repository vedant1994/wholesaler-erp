from decimal import Decimal
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from billing.models import Invoice
from .models import Payment, LedgerEntry, CustomerPayment
from .serializers import PaymentSerializer, LedgerEntrySerializer, CustomerPaymentSerializer
from .services import create_payment


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def payment_list_create_api(request):
    profile = getattr(request.user, "profile", None)

    if profile is None:
        raise PermissionDenied("User profile is not configured.")

    if request.method == "GET":
        if profile.role == "WHOLESALER":
            payments = Payment.objects.filter(invoice__wholesaler__user=request.user).select_related("invoice").order_by("-payment_date")
        elif profile.role == "RETAILER":
            payments = Payment.objects.filter(invoice__retailer__user=request.user).select_related("invoice").order_by("-payment_date")
        else:
            raise PermissionDenied("You cannot access payments.")

        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        if profile.role != "WHOLESALER":
            raise PermissionDenied("Only wholesalers can record invoice payments.")

        wholesaler = getattr(request.user, "wholesaler_profile", None)
        invoice_id = request.data.get("invoice")
        amount = request.data.get("amount")
        payment_method = request.data.get("payment_method")
        reference_number = request.data.get("reference_number", "")
        notes = request.data.get("notes", "")

        if not invoice_id or not amount or not payment_method:
            return Response({"error": "invoice, amount, and payment_method are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            invoice = Invoice.objects.get(id=invoice_id, wholesaler=wholesaler)
        except Invoice.DoesNotExist:
            raise NotFound("Invoice not found under your wholesaler account.")

        if invoice.status == "CANCELLED":
            return Response({"error": "Payments cannot be added to a cancelled invoice."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount_decimal = Decimal(str(amount))
            payment = create_payment(
                invoice_id=invoice.id,
                amount=amount_decimal,
                payment_method=payment_method,
                reference_number=reference_number,
                notes=notes,
            )
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PaymentSerializer(payment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def ledger_list_api(request):
    profile = getattr(request.user, "profile", None)

    if profile is None:
        raise PermissionDenied("User profile is not configured.")

    if profile.role == "WHOLESALER":
        entries = LedgerEntry.objects.filter(wholesaler__user=request.user).select_related("retailer", "invoice", "payment").order_by("-created_at")
    elif profile.role == "RETAILER":
        entries = LedgerEntry.objects.filter(retailer__user=request.user).select_related("wholesaler", "invoice", "payment").order_by("-created_at")
    else:
        raise PermissionDenied("You cannot access ledger entries.")

    serializer = LedgerEntrySerializer(entries, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def customer_payment_list_api(request):
    profile = getattr(request.user, "profile", None)

    if profile is None or profile.role != "RETAILER":
        raise PermissionDenied("Only retailers can access customer payments.")

    payments = CustomerPayment.objects.filter(invoice__retailer__user=request.user).select_related("invoice").order_by("-payment_date")
    serializer = CustomerPaymentSerializer(payments, many=True)
    return Response(serializer.data)
