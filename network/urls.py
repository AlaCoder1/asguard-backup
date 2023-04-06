from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('testPostNetwork', views.testPostNetwork, name="testPostNetwork"),
    path('testGetNetwork', views.testGetNetwork, name="testGetNetwork"),
]
