from django.urls import path
from . import views

urlpatterns = [
    ####### Server ######
    path('getAllServerOpenvpn', views.get_all_server_openvpn, name="getAllServerOpenvpn"),
    path('getServerOpenvpn/<int:id>', views.get_server_openvpn, name="getServerOpenvpn"),
    path('createServerOpenvpn', views.create_server_openvpn, name="createServerOpenvpn"),
    path('deleteServerOpenvpn/<int:id>', views.delete_server_openvpn, name="deleteServerOpenvpn"),
    path('updateServerOpenVPN/<int:id>', views.update_server_openvpn, name="updateServerOpenVPN"),
    path('startServerOpenvpn/<int:id>', views.start_server_openvpn, name="startServerOpenvpn"),
    path('restartServerOpenvpn/<int:id>', views.restart_server_openvpn, name="restartServerOpenvpn"),
    path('stopServerOpenvpn/<int:id>', views.stop_server_openvpn, name="stopServerOpenvpn"),
    
    ####### Client ######
    path('getAllClientOpenvpn', views.get_all_client_openvpn, name="getAllClientOpenvpn"),
    path('getClientOpenvpn/<int:id>', views.get_client_openvpn, name="getClientOpenvpn"),
    path('createClientOpenvpn', views.create_client_openvpn, name="createClientOpenvpn"),
    path('deleteClientOpenvpn/<int:id>', views.delete_client_openvpn, name="deleteClientOpenvpn"),
    path('updateClientOpenvpn/<int:id>', views.update_client_openvpn, name="updateClientOpenvpn"),
    path('exportClientOpenvpn/<int:id>', views.export_client_openvpn, name="exportClientOpenvpn"),
    path('generateClientOpenvpn/<int:id>', views.generate_client_openvpn, name="generateClientOpenvpn"),
]
