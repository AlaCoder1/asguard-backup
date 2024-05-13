from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('addStaticGateway', views.add_static_gateway, name="addStaticGateway"),
    path('updateGateway/<int:id>', views.update_gateway, name="updateGateway"),
    path('deleteGateway/<int:id>', views.delete_gateway, name="deleteGateway"),
    path('getGatewayById/<int:id>', views.get_gateway_by_id, name="getGatewayById"),
    path('getStaticGateways', views.get_all_static_gateways, name="getStaticGateways"),
    path('getAllGateways', views.get_all_gateways, name="getAllGateways"),
    
    
    
    

]
