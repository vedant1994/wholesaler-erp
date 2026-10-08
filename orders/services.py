from datetime import date
from decimal import Decimal

from django.db import transaction
from django.db.models import Q

from products.models import Stock, RetailerStock

from .models import Order

@transaction.atomic
def fulfill_order(order_id):

    order = (
        Order.objects
        .select_for_update()
        .get(id=order_id)
    )

    if order.status not in ["ACCEPTED", "WAITING_FOR_STOCK"]:
        return False

    today = date.today()

    allocations = []

    # --------------------------------
    # STEP 1: Check all order items
    # --------------------------------

    for item in order.items.select_related("product").all():

        remaining_quantity = item.quantity

        stocks = list(
            Stock.objects
            .select_for_update()
            .filter(
                product=item.product,
                quantity__gt=0
            )
            .filter(
                Q(expiry_date__isnull=True) |
                Q(expiry_date__gte=today)
            )
            .order_by(
                "expiry_date",
                "created_at"
            )
        )

        available_quantity = sum(
            (stock.quantity for stock in stocks),
            Decimal("0")
        )

        # Not enough stock
        if available_quantity < remaining_quantity:
            return False

        item_allocations = []

        # --------------------------------
        # Decide which stock rows to use
        # --------------------------------

        for stock in stocks:

            if remaining_quantity <= 0:
                break

            quantity_to_take = min(
                stock.quantity,
                remaining_quantity
            )

            item_allocations.append(
                (stock, quantity_to_take)
            )

            remaining_quantity -= quantity_to_take

        allocations.append(
            (item, item_allocations)
        )

    # --------------------------------
    # STEP 2: Deduct wholesaler stock
    # --------------------------------

    for item, item_allocations in allocations:

        for stock, quantity_to_take in item_allocations:

            stock.quantity -= quantity_to_take

            stock.save(
                update_fields=["quantity"]
            )

        # --------------------------------
        # STEP 3: Add retailer stock
        # --------------------------------

        retailer_stock, created = (
            RetailerStock.objects.get_or_create(
                retailer=order.retailer,
                product=item.product,
                defaults={
                    "quantity": Decimal("0")
                }
            )
        )

        retailer_stock.quantity += item.quantity

        retailer_stock.save(
            update_fields=[
                "quantity",
                "updated_at"
            ]
        )

    # --------------------------------
    # STEP 4: Change order status
    # --------------------------------

    order.status = "PROCESSING"

    order.save(
        update_fields=["status"]
    )

    return True