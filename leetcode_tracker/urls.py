from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from core.views import matrix_view, refresh_leetcode, admin_dashboard_stats

urlpatterns = [
    path("admin/dashboard-stats/", admin_dashboard_stats, name="admin_dashboard_stats"),
    path("admin/", admin.site.urls),
    path("", matrix_view, name="matrix"),
    path("refresh/", csrf_exempt(refresh_leetcode), name="refresh_leetcode"),
]
