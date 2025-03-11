from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('conf/<str:name_interface>', views.conf, name="conf"),
    # path('deleteInterface/<int:id>', views.delete_interface, name="deleteInterface"),
    path('AllInterfaces', views.AllInterfaces, name="AllInterfaces"),
    path('GetInformationsByInterface/<str:name_interface>', views.GetInformationsByInterface, name="GetInformationsByInterface"),
    

]
