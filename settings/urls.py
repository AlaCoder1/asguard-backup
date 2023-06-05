from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    
    # path('timezone', views.timezone, name="timezone"),
    # path('sys', views.sys, name="sys"),
    # path('ipv4', views.ipv4, name="ipv4"),
    # path('updateHostname', views.updateHostname, name="updateHostname"),
    # path('configurationNetwork', views.configurationNetwork, name="configurationNetwork"),
    # path('getInterface', views.getInterface, name="getInterface"),
    # path('deleteAddress', views.deleteAddress, name="deleteAddress"),
    # path('createFile', views.createFile, name="createFile"),
    # path('readFile', views.readFile, name="readFile"),
    
    path('<int:id>', views.Settings, name="Settings"),
    path('getSystem/<int:id>', views.getSystem, name="getSystem"),
    path('getNetwork/<int:id>', views.getNetwork, name="getNetwork"),
    path('getServerReseau/<int:id>', views.getServerReseau, name="getServerReseau"),
    path('createSystem', views.createSystem, name="createSystem"),
    path('createServerReseau', views.createServerReseau, name="createServer"),
    path('createNetwork', views.createNetwork, name="createNetwork"),
    path('initDBtimeZone', views.initDB_by_timeZone, name="initDBtimeZone"),
    path('timeZones', views.timeZones, name="timeZones"),
    path('InterfaceFromGateway', views.InterfaceFromGateway, name="InterfaceFromGateway"),
    path('AllGateway', views.AllGateway, name="AllGateway"),
    # path('deleteDB', views.deleteDB, name="deleteDB"),
    # path('deleteServer/<int:id>', views.deleteServer, name="deleteServer"),
    # path('modifyServer/<int:id>', views.modifyServer, name="modifyServer"),
]
