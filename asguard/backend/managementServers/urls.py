from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('getAllServers', views.get_all_servers, name="getAllServers"),
    path('getServer/<int:id>', views.get_server, name="getServer"),
    path('createServer', views.create_server, name="createServer"),
    path('deleteServer/<int:id>', views.delete_server, name="deleteServer"),
    path('modifyServer/<int:id>', views.modify_server, name="modifyServer"),
]
