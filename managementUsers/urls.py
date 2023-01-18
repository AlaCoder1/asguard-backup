from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('getAllUsers', views.getAllUsers, name="getAllUsers"),
    path('createUser', views.createUser, name="createUser"),
    path('userDetails', views.userDetails, name="userDetails"),
]