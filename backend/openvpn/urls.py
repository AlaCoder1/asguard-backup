from django.urls import path
from . import views_server, views_client

urlpatterns = [
    ####### Server ######
    path('getAllServerOpenvpn', views_server.get_all_server_openvpn, name="getAllServerOpenvpn"),
    path('getServerOpenvpn/<int:id>', views_server.get_server_openvpn, name="getServerOpenvpn"),
    path('createServerOpenvpn', views_server.create_server_openvpn, name="createServerOpenvpn"),
    path('deleteServerOpenvpn/<int:id>', views_server.delete_server_openvpn, name="deleteServerOpenvpn"),
    path('updateServerOpenVPN/<int:id>', views_server.update_server_openvpn, name="updateServerOpenVPN"),
    path('startServerOpenvpn/<int:id>', views_server.start_server_openvpn, name="startServerOpenvpn"),
    path('restartServerOpenvpn/<int:id>', views_server.restart_server_openvpn, name="restartServerOpenvpn"),
    path('stopServerOpenvpn/<int:id>', views_server.stop_server_openvpn, name="stopServerOpenvpn"),
    
    ####### Client ######
    path('getAllClientOpenvpn', views_client.get_all_client_openvpn, name="getAllClientOpenvpn"),
    path('getClientOpenvpn/<int:id>', views_client.get_client_openvpn, name="getClientOpenvpn"),
    path('createClientOpenvpn', views_client.create_client_openvpn, name="createClientOpenvpn"),
    path('deleteClientOpenvpn/<int:id>', views_client.delete_client_openvpn, name="deleteClientOpenvpn"),
    path('updateClientOpenvpn/<int:id>', views_client.update_client_openvpn, name="updateClientOpenvpn"),
    path('exportClientOpenvpn/<int:id>', views_client.export_client_openvpn, name="exportClientOpenvpn"),
    path('generateClientOpenvpn/<int:id>', views_client.generate_client_openvpn, name="generateClientOpenvpn"),
]
