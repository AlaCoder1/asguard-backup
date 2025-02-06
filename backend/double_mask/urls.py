from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('activate', views.activate_double_mask, name="activate"),
    path('deactivate', views.deactivate_double_mask, name="deactivate"),
    path('getstatus', views.get_double_mask, name="getstatus"),
   
]