from django.contrib import admin
from .models import Shipment

@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ("order", "courier", "tracking_number", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("order__id", "tracking_number", "courier")
