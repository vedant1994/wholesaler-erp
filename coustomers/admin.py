from django.contrib import admin
from .models import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "retailer", "created_at")
    search_fields = ("name", "phone", "retailer__shop_name")
