from django.urls import path
from . import views

urlpatterns = [
     path('getAllDhcp4Server', views.get_all_server_dhcp4, name="getAllDhcp4Server"),
     path('addDhcp4Server', views.add_server_dhcp4, name="addDhcp4Server"),
     path('deleteDhcp4Server/<int:server_id>', views.delete_server_dhcp4, name="getAllDhcp4Server"),
     path('updateDhcp4Server/<int:id_server>', views.update_config_dhcp4_server, name="updateDhcp4Server"),
     
]