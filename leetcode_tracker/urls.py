from django.contrib import admin
from django.urls import path
from core.views import matrix_view, refresh_leetcode

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", matrix_view, name="matrix"),
    path('refresh/', refresh_leetcode, name='refresh_leetcode')
]
