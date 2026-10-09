from django.urls import path
from .api_views import (
    register_api,
    login_api,
    logout_api,
    user_profile_api,
    dashboard_stats_api,
    retailer_list_api,
    notification_list_api,
    mark_notification_read_api,
)

urlpatterns = [
    path("register/", register_api, name="api_register"),
    path("login/", login_api, name="api_login"),
    path("logout/", logout_api, name="api_logout"),
    path("profile/", user_profile_api, name="api_user_profile"),
    path("dashboard-stats/", dashboard_stats_api, name="api_dashboard_stats"),
    path("retailers/", retailer_list_api, name="api_retailer_list"),
    path("notifications/", notification_list_api, name="api_notification_list"),
    path("notifications/<int:notification_id>/read/", mark_notification_read_api, name="api_mark_notification_read"),
]
