from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
     path('CreateServer', views.connect_to_ad, name="Create_AD_Server"),
     path('updateldap_Server/<int:id>', views.updateLdapServer, name="updateGateway"),
     path('deleteldap_Server/<int:id>', views.deleteldap_server, name="deleteGateway"),
     path('getldap_ServerById/<int:id>', views.getServerById, name="getGatewayById"),
     path('getAllldap_Servers', views.get_all_servers, name="getAllGateways"),

    
]
