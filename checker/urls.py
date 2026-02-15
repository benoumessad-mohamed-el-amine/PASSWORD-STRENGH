"""
URL configuration for checker app.
"""
from django.urls import path
from . import views

app_name = 'checker'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/check/', views.check_password, name='check_password'),
]
