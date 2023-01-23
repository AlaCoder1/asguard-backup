from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('getAllUsers', views.getAllUsers, name="getAllUsers"),
    path('createUser', views.createUser, name="createUser"),
    path('deleteUser', views.delete_user, name="deleteUser"),
    path('userDetails', views.userDetails, name="userDetails"),
    path('userChangePW', views.change_password, name="userChangePW"),
    path('userChangeUsername', views.change_username, name="userChangeUsername"),
]
