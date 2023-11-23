from django.urls import path
from . import views

urlpatterns = [
    ####### Server ######
    path('getAllServerOpenvpn', views.getAllServerOpenvpn, name="getAllServerOpenvpn"),
    path('getServerOpenvpn/<int:id>', views.getServerOpenvpn, name="getServerOpenvpn"),
    path('createServerOpenvpn', views.createServerOpenvpn, name="createServerOpenvpn"),
    path('deleteServerOpenvpn/<int:id>', views.deleteServerOpenvpn, name="deleteServerOpenvpn"),
    path('updateServerOpenVPN/<int:id>', views.updateServerOpenVPN, name="updateServerOpenVPN"),
    path('startServerOpenvpn/<int:id>', views.startServerOpenvpn, name="startServerOpenvpn"),
    path('restartServerOpenvpn/<int:id>', views.restartServerOpenvpn, name="restartServerOpenvpn"),
    path('stopServerOpenvpn/<int:id>', views.stopServerOpenvpn, name="stopServerOpenvpn"),
    
    ####### Client ######
    path('getAllClientOpenvpn', views.getAllClientOpenvpn, name="getAllClientOpenvpn"),
    path('getClientOpenvpn/<int:id>', views.getClientOpenvpn, name="getClientOpenvpn"),
    path('createClientOpenvpn', views.createClientOpenvpn, name="createClientOpenvpn"),
    path('deleteClientOpenvpn/<int:id>', views.deleteClientOpenvpn, name="deleteClientOpenvpn"),
    path('updateClientOpenvpn/<int:id>', views.updateClientOpenvpn, name="updateClientOpenvpn"),
    path('exportClientOpenvpn/<int:id>', views.exportClientOpenvpn, name="exportClientOpenvpn"),
]
