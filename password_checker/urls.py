"""
URL configuration for password_checker project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('checker.urls')),  # Include checker app URLs
]
