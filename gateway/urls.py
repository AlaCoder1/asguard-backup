from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('addStaticGateway', views.addStaticGateway, name="addStaticGateway"),
    path('updateGateway/<int:id>', views.updateGateway, name="updateGateway"),
    path('deleteGateway/<int:id>', views.deleteGateway, name="deleteGateway"),
    path('getGatewayById/<int:id>', views.getGatewayById, name="getGatewayById"),
    path('getStaticGateways', views.getAllStaticGateways, name="getStaticGateways"),
    path('getAllGateways', views.getAllGateways, name="getAllGateways"),
    
    
    
    

]
