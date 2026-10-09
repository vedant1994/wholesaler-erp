from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import (RegistrationForm, WholesalerProfileForm, RetailerProfileForm)
from django.db.models import F, Sum
from datetime import date, timedelta
from products.models import Product, Stock
from orders.models import Order
from billing.models import Invoice
from payments.models import Payment, LedgerEntry
from .models import UserProfile, WholesalerProfile, RetailerProfile, Notification

from decimal import Decimal

# Create your views here.

def register(request):

    if request.method == "POST":

        form = RegistrationForm(request.POST)

        if form.is_valid():

            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            role = form.cleaned_data["role"]

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            UserProfile.objects.create(
                user=user,
                role=role
            )

            if role == "WHOLESALER":

                WholesalerProfile.objects.create(
                    user=user,
                    business_name=username,
                    phone="",
                    address="",
                    city="",
                    state="",
                    pincode=""
                )

            elif role == "RETAILER":

                RetailerProfile.objects.create(
                    user=user,
                    shop_name=username,
                    owner_name=username,
                    phone="",
                    address="",
                    city="",
                    state="",
                    pincode=""
                )

            # Login AFTER creating the profile
            login(request, user)

            # Redirect for BOTH wholesaler and retailer
            return redirect("dashboard")

    else:

        form = RegistrationForm()

    return render(
        request,
        "accounts/register.html",
        {"form": form}
    )

def user_login(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect("dashboard")

        else:

            return render(
                request,
                "accounts/login.html",
                {
                    "error": "Invalid username or password."
                }
            )

    return render(
        request,
        "accounts/login.html"
    )

def user_logout(request):

    logout(request)

    return redirect("login")


@login_required
def dashboard(request):
    profile = getattr(request.user, 'profile', None)
    if not profile:
        # Default or fallback if UserProfile was not initialized
        return redirect("login")

    today = date.today()
    expiry_limit = today + timedelta(days=30)

    if profile.role == "WHOLESALER":
        wholesaler = request.user.wholesaler_profile
        
        # Real statistics queries
        total_products = Product.objects.filter(wholesaler=wholesaler).count()
        low_stock_count = Stock.objects.filter(
            product__wholesaler=wholesaler,
            quantity__lte=F("minimum_stock")
        ).count()
        expiring_count = Stock.objects.filter(
            product__wholesaler=wholesaler,
            expiry_date__isnull=False,
            expiry_date__gte=today,
            expiry_date__lte=expiry_limit
        ).count()
        pending_orders_count = Order.objects.filter(
            wholesaler=wholesaler,
            status="PENDING"
        ).count()
        total_retailers = wholesaler.retailers.count()

        # Calculate total outstanding across all invoices (deducting payments)
        invoices = Invoice.objects.filter(wholesaler=wholesaler, status__in=["UNPAID", "PARTIALLY_PAID"]).prefetch_related("payments")
        total_outstanding = Decimal("0.00")
        for inv in invoices:
            total_paid_for_inv = sum((p.amount for p in inv.payments.all()), Decimal("0.00"))
            outstanding_for_inv = inv.grand_total - total_paid_for_inv
            if outstanding_for_inv > Decimal("0.00"):
                total_outstanding += outstanding_for_inv
            else:
                inv.status = "PAID"
                inv.save(update_fields=["status"])

        recent_orders = (
            Order.objects.filter(wholesaler=wholesaler)
            .select_related("retailer")
            .order_by("-order_date")[:5]
        )
        recent_invoices = (
            Invoice.objects.filter(wholesaler=wholesaler)
            .select_related("retailer")
            .order_by("-invoice_date")[:5]
        )

        context = {
            "wholesaler": wholesaler,
            "total_products": total_products,
            "low_stock_count": low_stock_count,
            "expiring_count": expiring_count,
            "pending_orders_count": pending_orders_count,
            "total_retailers": total_retailers,
            "total_outstanding": total_outstanding,
            "recent_orders": recent_orders,
            "recent_invoices": recent_invoices,
        }

        return render(request, "accounts/wholesaler_dashboard.html", context)

    elif profile.role == "RETAILER":
        retailer = request.user.retailer_profile

        # Real statistics queries for retailer
        total_orders = Order.objects.filter(retailer=retailer).count()
        pending_orders_count = Order.objects.filter(retailer=retailer, status="PENDING").count()
        recent_orders = (
            Order.objects.filter(retailer=retailer)
            .select_related("wholesaler")
            .order_by("-order_date")[:5]
        )
        recent_invoices = (
            Invoice.objects.filter(retailer=retailer)
            .select_related("wholesaler")
            .order_by("-invoice_date")[:5]
        )

        # Real-time total spent (sum of all payments made to suppliers)
        total_spent = Payment.objects.filter(invoice__retailer=retailer).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

        # Real-time actual unpaid balance across all supplier invoices
        unpaid_invoices = Invoice.objects.filter(
            retailer=retailer,
            status__in=["UNPAID", "PARTIALLY_PAID"]
        ).prefetch_related("payments")

        total_unpaid = Decimal("0.00")
        for inv in unpaid_invoices:
            total_paid_for_inv = sum((p.amount for p in inv.payments.all()), Decimal("0.00"))
            outstanding_for_inv = inv.grand_total - total_paid_for_inv
            if outstanding_for_inv > Decimal("0.00"):
                total_unpaid += outstanding_for_inv
            else:
                inv.status = "PAID"
                inv.save(update_fields=["status"])

        connected_wholesalers_count = retailer.wholesalers.count()

        context = {
            "retailer": retailer,
            "total_orders": total_orders,
            "pending_orders_count": pending_orders_count,
            "recent_orders": recent_orders,
            "recent_invoices": recent_invoices,
            "total_spent": total_spent,
            "total_unpaid": total_unpaid,
            "connected_wholesalers_count": connected_wholesalers_count,
        }

        return render(request, "accounts/retailer_dashboard.html", context)

@login_required
def retailer_list(request):
    profile = getattr(request.user, 'profile', None)
    if profile and profile.role == "WHOLESALER":
        wholesaler = request.user.wholesaler_profile
        retailers = wholesaler.retailers.all()
    else:
        retailers = RetailerProfile.objects.all()

    return render(request, "accounts/retailer_list.html", {"retailers": retailers})

@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "accounts/notifications.html", {"notifications": notifications})

@login_required
def reports_view(request):
    profile = getattr(request.user, 'profile', None)
    if profile and profile.role == "WHOLESALER":
        wholesaler = request.user.wholesaler_profile
        total_sales = Invoice.objects.filter(wholesaler=wholesaler, status="PAID").aggregate(total=Sum("grand_total"))["total"] or 0
        total_orders_count = Order.objects.filter(wholesaler=wholesaler).count()
        completed_orders_count = Order.objects.filter(wholesaler=wholesaler, status="DELIVERED").count()
        total_invoices_count = Invoice.objects.filter(wholesaler=wholesaler).count()
        paid_invoices_count = Invoice.objects.filter(wholesaler=wholesaler, status="PAID").count()
        unpaid_invoices_count = Invoice.objects.filter(wholesaler=wholesaler, status__in=["UNPAID", "PARTIALLY_PAID"]).count()
        
        context = {
            "role": "WHOLESALER",
            "total_sales": total_sales,
            "total_orders_count": total_orders_count,
            "completed_orders_count": completed_orders_count,
            "total_invoices_count": total_invoices_count,
            "paid_invoices_count": paid_invoices_count,
            "unpaid_invoices_count": unpaid_invoices_count,
        }
    elif profile and profile.role == "RETAILER":
        retailer = request.user.retailer_profile
        total_purchases = Invoice.objects.filter(retailer=retailer, status="PAID").aggregate(total=Sum("grand_total"))["total"] or 0
        total_orders_count = Order.objects.filter(retailer=retailer).count()
        pending_orders_count = Order.objects.filter(retailer=retailer, status="PENDING").count()
        total_invoices_count = Invoice.objects.filter(retailer=retailer).count()

        context = {
            "role": "RETAILER",
            "total_purchases": total_purchases,
            "total_orders_count": total_orders_count,
            "pending_orders_count": pending_orders_count,
            "total_invoices_count": total_invoices_count,
        }
    else:
        context = {}

    return render(request, "reports/reports.html", context)

