from django.urls import path
from .views import (register, user_login, user_logout, dashboard, retailer_list, notifications_view)

urlpatterns = [
    path("register/", register, name="register"),
    path("login/", user_login, name="login"),
    path("logout/", user_logout, name="logout"),
    path("dashboard/", dashboard, name="dashboard"),
    path("retailers/", retailer_list, name="retailer_list"),
    path("notifications/", notifications_view, name="notifications"),
]