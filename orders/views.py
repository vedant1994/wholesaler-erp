from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from accounts.models import WholesalerProfile
from products.models import Product

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