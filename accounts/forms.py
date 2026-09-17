from django import forms
from django.contrib.auth.models import User
from .models import (UserProfile, WholesalerProfile, RetailerProfile)

class RegistrationForm(forms.Form):

    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(
        widget=forms.PasswordInput
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput
    )
    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES
    )

    def clean_username(self):
        username = self.cleaned_data["username"]

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "Username already exists."
            )

        return username

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError(
                    "Passwords do not match."
                )

        return cleaned_data

class WholesalerProfileForm(forms.ModelForm):

    class Meta:
        model = WholesalerProfile

        fields = [
            "business_name", "phone","gst_number","address","city","state","pincode",
        ]

class RetailerProfileForm(forms.ModelForm):

    class Meta:
        model = RetailerProfile

        fields = [
            "shop_name","owner_name","phone","gst_number","address","city","state","pincode",
        ]