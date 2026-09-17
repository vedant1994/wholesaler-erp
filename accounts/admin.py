from django.contrib import admin
from .models import (UserProfile, WholesalerProfile, RetailerProfile)

# Register your models here.

@admin.register(UserProfile)
class UserProfleAdmin(admin.ModelAdmin):
    list_display=("user", "role", "created_at")
    list_filter=("role",)

@admin.register(WholesalerProfile)
class WholesalerProfileAdmin(admin.ModelAdmin):
    list_display=("business_name", "user","phone","gst_number","city","state")

@admin.register(RetailerProfile)
class RetailerProfileAdmin(admin.ModelAdmin):
    list_display=("shop_name", "owner_name","user","phone","gst_number","city","state")

