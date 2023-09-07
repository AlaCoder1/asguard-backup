from django.contrib import admin
from django.urls import path
from . import views1
from . import viewsVersion2

urlpatterns = [
     path('conf/<str:name_interface>', viewsVersion2.conf, name="conf"),
    # path('addInterface', viewsVersion2.add_interface, name="addInterface"),
    path('conf/<int:id>', viewsVersion2.conf, name="conf"),
    path('deleteInterface/<int:id>', viewsVersion2.delete_interface, name="deleteInterface"),
    path('AllInterfaces', viewsVersion2.AllInterfaces, name="AllInterfaces"),
    path('GetInformationsByInterface/<str:name_interface>', viewsVersion2.GetInformationsByInterface, name="GetInformationsByInterface"),
    

]
