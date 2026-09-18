from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction

from accounts.models import WholesalerProfile
from products.models import Product

from .models import Order, OrderItem
from .forms import CreateOrderForm

# Create your views here.

@login_required
def wholesaler_list(request):

    retailer = request.user.retailer_profile

    wholesalers = WholesalerProfile.objects.all()

    return render(
        request,
        "orders/wholesaler_list.html",
        {
            "wholesalers": wholesalers
        }
    )

@login_required
def wholesaler_products(request, wholesaler_id):

    retailer = request.user.retailer_profile

    wholesaler = get_object_or_404(
        WholesalerProfile,
        id = wholesaler_id,
        retailers = retailer
    )

    products = Product.objects.filter(
        wholesaler = wholesaler
    )

    return render(
        request,
        "orders/wholesaler_products.html",
        {
            "wholesaler": wholesaler,
            "products": products,
        }
    )

@login_required
def create_order(request, wholesaler_id, product_id):

    retailer = request.user.retailer_profile

    wholesaler = get_object_or_404(
        WholesalerProfile,
        id=wholesaler_id,
        retailers=retailer
    )

    product = get_object_or_404(
        Product,
        id=product_id,
        wholesaler=wholesaler
    )

    form = CreateOrderForm()

    if request.method == "POST":

        form = CreateOrderForm(request.POST)

        if form.is_valid():

            quantity = form.cleaned_data["quantity"]
            notes = form.cleaned_data["notes"]

            stock = product.stocks.order_by("-created_at").first()

            if stock is None:

                form.add_error(
                    None,
                    "This product currently has no stock."
                )

            else:

                price_per_unit = stock.selling_price
                total_price = quantity * price_per_unit

                with transaction.atomic():

                    order = Order.objects.create(
                        retailer=retailer,
                        wholesaler=wholesaler,
                        status="PENDING",
                        notes=notes
                    )

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price_per_unit=price_per_unit,
                        total_price=total_price
                    )

                return redirect(
                    "order_detail",
                    order_id=order.id
                )

    return render(
        request,
        "orders/create_order.html",
        {
            "form": form,
            "product": product,
            "wholesaler": wholesaler,
            "stock": product.stocks.order_by("-created_at").first(),
        }
    )

@login_required
def my_orders(request):
    retailer = request.user.retailer_profile

    orders = (
        Order.objects
        .filter(retailer = retailer)
        .select_related("wholesaler")
        .prefetch_related("items__product")
        .order_by("-order_date")
    )

    return render(
        request,
        'orders/my_orders.html',
        {
            "orders": orders
        }
    )

@login_required
def order_detail(request, order_id):

    retailer = request.user.retailer_profile

    order = get_object_or_404(
        Order.objects
        .select_related("wholesaler")
        .prefetch_related("items__product"),
        id=order_id,
        retailer=retailer
    )

    return render(
        request,
        "orders/order_detail.html",
        {"order": order}
    )