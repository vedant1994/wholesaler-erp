from django.db.models import Sum, Count, F, Q
from accounts.models import WholesalerProfile, RetailerProfile
from billing.models import Invoice
from products.models import Product
from orders.models import Order

def get_wholesaler_dashboard_stats(wholesaler):
    # Total Retailers connected
    total_retailers = wholesaler.retailers.count()

    # Total Stock Value (quantity * price)
    from products.models import Stock
    total_stock_value = Stock.objects.filter(product__wholesaler=wholesaler).aggregate(
        total_value=Sum(F('quantity') * F('selling_price'))
    )['total_value'] or 0

    # Low stock items count
    low_stock_items = Stock.objects.filter(
        product__wholesaler=wholesaler, 
        quantity__lte=F('minimum_stock')
    ).count()

    # Pending Orders
    pending_orders = Order.objects.filter(wholesaler=wholesaler, status='PENDING').count()
    
    # Outstanding Amount
    total_outstanding = 0
    for retailer in wholesaler.retailers.all():
        total_outstanding += wholesaler.get_outstanding_for_retailer(retailer)

    return {
        "total_retailers": total_retailers,
        "total_stock_value": total_stock_value,
        "low_stock_items": low_stock_items,
        "pending_orders": pending_orders,
        "total_outstanding": total_outstanding
    }

def get_retailer_dashboard_stats(retailer):
    # Connected wholesalers
    total_wholesalers = retailer.wholesalers.count()

    # Total customers
    from coustomers.models import Customer
    total_customers = Customer.objects.filter(retailer=retailer).count()

    # Total outstanding payable to wholesalers
    total_payable = 0
    for wholesaler in retailer.wholesalers.all():
        total_payable += retailer.get_outstanding_for_wholesaler(wholesaler)

    return {
        "total_wholesalers": total_wholesalers,
        "total_customers": total_customers,
        "total_payable": total_payable
    }
