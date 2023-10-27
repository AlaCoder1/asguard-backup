from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('getAllServers', views.getAllServers, name="getAllServers"),
    path('getServer/<int:id>', views.getServer, name="getServer"),
    path('createServer', views.createServer, name="createServer"),
    path('deleteServer/<int:id>', views.deleteServer, name="deleteServer"),
    path('modifyServer/<int:id>', views.modifyServer, name="modifyServer"),
]
