from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import F, Q
from datetime import date, timedelta
from .forms import ProductForm, StockForm
from .models import Product, Stock

# Create your views here.

@login_required
def add_product(request):

    if request.method == "POST":
        form = ProductForm(request.POST)

        if form.is_valid():
            product = form.save(commit=False)
            product.wholesaler = request.user.wholesaler_profile
            product.save()
            return redirect("product_list")
    else:
        form = ProductForm()

    return render(
        request,
        "products/add_product.html",
        {"form": form}
    )

@login_required
def product_list(request):

    wholesaler = request.user.wholesaler_profile

    products = Product.objects.filter(
        wholesaler=wholesaler
    )

    return render(request, "products/product_list.html", {"products" : products})

@login_required
def edit_product(request, product_id):

    wholesaler = request.user.wholesaler_profile

    product = get_object_or_404(
        Product,
        id = product_id,
        wholesaler = wholesaler
    )

    if request.method == "POST":

        form = ProductForm(request.POST, instance=product)

        if form.is_valid():
            form.save()
            return redirect("product_list")

    else:
        form = ProductForm(instance=product)

    return render(
        request,
        "products/edit_product.html",
        {"form": form, "product": product}
    )

@login_required
def delete_product(request, product_id):

    wholesaler = request.user.wholesaler_profile

    product = get_object_or_404(
        Product,
        id=product_id,
        wholesaler=wholesaler
    )

    if request.method == "POST":
        product.delete()

        return redirect("product_list")

    return render(
        request,
        "products/delete_product.html",
        {"product": product}
    )

@login_required
def add_stock(request):

    wholesaler = request.user.wholesaler_profile

    if request.method == "POST":

        form = StockForm(
            request.POST,
            wholesaler = wholesaler
        )

        if form.is_valid():
            stock = form.save()
            return redirect("stock_list")

    else:
        form = StockForm(
            wholesaler=wholesaler
        )

    return render(
        request,
        "products/add_stock.html",
        {"form": form}
    )

@login_required
def stock_list(request):

    wholesaler = request.user.wholesaler_profile

    stocks = Stock.objects.filter(
        product__wholesaler = wholesaler,
    ).select_related("product")

    categories = Product.objects.filter(
        wholesaler = wholesaler
    ).values_list(
        "category",
        flat=True
    ).distinct()

    search = request.GET.get("search", "")

    if search:
        stocks = stocks.filter(
            Q(product__name__icontains = search) |
            Q(product__sku__icontains = search)
        )

    category = request.GET.get("category", "")

    if category:
        stocks = stocks.filter(
            product__category = category
        )

    stock_status = request.GET.get("stock_status", "")

    if stock_status == "low":
        stocks = stocks.filter(
            quantity__lte = F("minimum_stock")
        )

    elif stock_status == "in_stock":
        stocks = stocks.filter(
            quantity__gt = F("minimum_stock")
        )

    for stock in stocks:
        if stock.quantity <= stock.minimum_stock:
            stock.is_low_stock = True
        else:
            stock.is_low_stock = False

    today = date.today()
    expiry_limit = today + timedelta(days=30)

    for stock in stocks:

        if stock.expiry_date is None:
            stock.expiry_status = "NO EXPIRY DATE"

        elif stock.expiry_date < today:
            stock.expiry_status = "EXPIRED"

        elif stock.expiry_date <= expiry_limit:
            stock.expiry_status = "SOON EXPIRING"

        else:
            stock.expiry_status = "GOOD"

    expiry_status = request.GET.get("expiry_status", "")

    if expiry_status == "expired":
        stocks = stocks.filter(
            expiry_date__lt=today
        )

    elif expiry_status == "soon_expiring":
        stocks = stocks.filter(
            expiry_date__gte=today,
            expiry_date__lte=expiry_limit
        )

    elif expiry_status == "good":
        stocks = stocks.filter(
            expiry_date__gt=expiry_limit
        )

    return render(
        request,
        "products/stock_list.html",
        {
            "stocks": stocks,
            "categories": categories,
            "search": search,
            "selected_category": category,
            "selected_stock_status": stock_status,
            "selected_expiry_status": expiry_status,
        }
    )

@login_required
def edit_stock(request, stock_id):

    wholesaler = request.user.wholesaler_profile

    stock = get_object_or_404(
        Stock,
        id=stock_id,
        product__wholesaler=wholesaler
    )

    if request.method == "POST":

        form = StockForm(request.POST, instance=stock, wholesaler=wholesaler)

        if form.is_valid():
            form.save()
            return redirect("stock_list")

    else:
        form = StockForm(instance=stock, wholesaler=wholesaler)

    return render(
        request,
        "products/edit_stock.html",
        {"form": form, "stock": stock}
    )

@login_required
def delete_stock(request, stock_id):

    wholesaler = request.user.wholesaler_profile

    stock = get_object_or_404(
        Stock,
        id=stock_id,
        product__wholesaler=wholesaler
    )

    if request.method == "POST":
        stock.delete()

        return redirect("stock_list")

    return render(
        request,
        "products/delete_stock.html",
        {"stock": stock}
    )

@login_required
def low_stock_list(request):

    wholesaler = request.user.wholesaler_profile

    low_stocks = Stock.objects.filter(
        product__wholesaler = wholesaler,
        quantity__lte = F("minimum_stock")
    ).select_related("product")

    return render(
        request,
        "products/low_stock_list.html",
        {"low_stocks" : low_stocks}
    )

@login_required
def expiry_list(request):

    wholesaler = request.user.wholesaler_profile

    today = date.today()

    expiry_limit = today + timedelta(days=30)

    stocks = Stock.objects.filter(
        product__wholesaler = wholesaler,
        expiry_date__isnull = False,
        expiry_date__lte = expiry_limit
    ).select_related("product")

    for stock in stocks:

        if stock.expiry_date < today:
            stock.expiry_status = "EXPIRED"

        else:
            stock.expiry_status = "EXPIRING SOON"

        return render(
        request,
        "products/expiry_list.html",
        {"stocks": stocks, "today": today}
    )

@login_required
def retailer_stock_list(request):
    profile = getattr(request.user, 'profile', None)
    if profile and profile.role == "RETAILER":
        retailer = request.user.retailer_profile
        stocks = Stock.objects.filter(product__wholesaler__in=retailer.wholesalers.all()).select_related("product")
    else:
        stocks = Stock.objects.none()

    return render(request, "products/stock_list.html", {"stocks": stocks})