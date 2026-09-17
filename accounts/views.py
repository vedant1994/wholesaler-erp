from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import (UserProfile, WholesalerProfile, RetailerProfile)
from .forms import (RegistrationForm, WholesalerProfileForm, RetailerProfileForm)

# Create your views here.

def register(request):

    if request.method == "POST":

        form = RegistrationForm(request.POST)

        if form.is_valid():

            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            role = form.cleaned_data["role"]

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            UserProfile.objects.create(
                user=user,
                role=role
            )

            if role == "WHOLESALER":

                WholesalerProfile.objects.create(
                    user=user,
                    business_name=username,
                    phone="",
                    address="",
                    city="",
                    state="",
                    pincode=""
                )

            elif role == "RETAILER":

                RetailerProfile.objects.create(
                    user=user,
                    shop_name=username,
                    owner_name=username,
                    phone="",
                    address="",
                    city="",
                    state="",
                    pincode=""
                )

            # Login AFTER creating the profile
            login(request, user)

            # Redirect for BOTH wholesaler and retailer
            return redirect("dashboard")

    else:

        form = RegistrationForm()

    return render(
        request,
        "accounts/register.html",
        {"form": form}
    )

def user_login(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect("dashboard")

        else:

            return render(
                request,
                "accounts/login.html",
                {
                    "error": "Invalid username or password."
                }
            )

    return render(
        request,
        "accounts/login.html"
    )

def user_logout(request):

    logout(request)

    return redirect("login")

@login_required
def dashboard(request):

    profile = request.user.profile

    if profile.role == "WHOLESALER":
        wholesaler = request.user.wholesaler_profile
        return render(request, "accounts/wholesaler_dashboard.html", {"wholesaler":wholesaler})

    elif profile.role == "RETAILER":
        retailer = request.user.retailer_profile

        return render(request, "accounts/retailer_dashboard.html",{"retailer": retailer})