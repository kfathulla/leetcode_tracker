from django.contrib import admin
from django.urls import path
from core.views import matrix_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", matrix_view),
]
