from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserProfile(models.Model):

    ROLE_CHOICES=[
        ('WHOLESALER', 'Wholesaler'),
        ('RETAILER', 'Retailer'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class WholesalerProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wholesaler_profile")
    business_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    gst_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    retailers = models.ManyToManyField("RetailerProfile",related_name="wholesalers",blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.business_name

class RetailerProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="retailer_profile"
    )

    shop_name = models.CharField(max_length=200)
    owner_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    gst_number = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )
    
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.shop_name