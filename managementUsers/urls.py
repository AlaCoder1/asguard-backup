from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('whoami', views.whoami, name="whoami"),
    path('handle', views.handle, name="handle"),
    path('getAllUsers', views.getAllUsers, name="getAllUsers"),
    path('getUser/<int:id>', views.getUser, name="getUser"),
    path('createUser', views.createUser, name="createUser"),
    path('deleteUser/<int:id>', views.delete_user, name="deleteUser"),
    path('modifyUser/<int:id>', views.modifyUser, name="modifyUser"),
    path('addPermission', views.addPermission, name="addPermission"),
    path('userChangePW', views.changePassword, name="userChangePW"),
]

