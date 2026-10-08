"""Service layer for the coustomers app.
Provides pure business‑logic functions that the views can call.
Keeping this separate from the views makes the code easier to test and keeps the view functions thin – just handling HTTP & templates.
"""

from .models import Customer
from django.shortcuts import get_object_or_404


def get_all_customers():
    """Return a QuerySet of all Customer objects."""
    return Customer.objects.select_related("retailer").all()


def get_customer(pk):
    """Retrieve a single Customer or raise 404 if not found."""
    return get_object_or_404(Customer, pk=pk)


def create_customer(data):
    """Create a Customer from a dict of validated data.
    ``data`` is expected to contain the fields used by ``CustomerForm``.
    """
    return Customer.objects.create(**data)


def update_customer(pk, data):
    """Update an existing Customer with ``data`` dict and return the instance."""
    customer = get_customer(pk)
    for attr, value in data.items():
        setattr(customer, attr, value)
    customer.save()
    return customer


def delete_customer(pk):
    """Delete a Customer and return ``True`` on success."""
    customer = get_customer(pk)
    customer.delete()
    return True
