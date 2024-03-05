from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
     path('CreateServer', views.connect_to_ad, name="Create_AD_Server"),
    
]
