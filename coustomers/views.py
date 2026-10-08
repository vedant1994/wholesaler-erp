from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from .models import Customer

# List all customers for a wholesaler
class CustomerListView(ListView):
    model = Customer
    template_name = "coustomers/customer_list.html"
    context_object_name = "customers"
    paginate_by = 20

# Show a single customer's details
class CustomerDetailView(DetailView):
    model = Customer
    template_name = "coustomers/customer_detail.html"
    context_object_name = "customer"

# Create a new customer record
class CustomerCreateView(CreateView):
    model = Customer
    fields = ["retailer", "name", "phone", "email", "address", "gst_number"]
    template_name = "coustomers/customer_form.html"
    success_url = reverse_lazy("customer_list")

# Update an existing customer
class CustomerUpdateView(UpdateView):
    model = Customer
    fields = ["name", "phone", "email", "address", "gst_number"]
    template_name = "coustomers/customer_form.html"
    success_url = reverse_lazy("customer_list")
