from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('getAllUsers', views.getAllUsers, name="getAllUsers"),
    path('getUser/<int:id>', views.getUser, name="getUser"),
    path('createUser', views.createUser, name="createUser"),
    path('deleteUser/<int:id>', views.delete_user, name="deleteUser"),
    path('modifyUser/<int:id>', views.modifyUser, name="modifyUser"),
    path('addPermission', views.addPermission, name="addPermission"),
    path('userChangePW', views.changePassword, name="userChangePW"),
    path('authentification', views.authentification, name="authentification"),
    path('authentification2', views.authentifacation2, name="authentification2"),
    path('authentification_JWT',views.authentification_JWT,name="authentification_JWT"),
    path('logout',views.logout_view,name="logout")
]

