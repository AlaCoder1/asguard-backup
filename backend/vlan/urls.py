from django.urls import path
from . import views

urlpatterns = [
     path('addVlan', views.add_vlan, name="addVlan"),
     path('updateVlan/<int:id>', views.update_vlan, name="updateVlan"),
     path('deleteVlan/<int:id>', views.delete_vlan, name="deleteVlan"),
     path('getAllVlan', views.get_vlan, name="getAllVlan"),
     path('getVlanInterface', views.get_vlan_interface, name="getVlanInterface"),
     path('assignVlanInterface', views.assign_vlan_interface, name="assignVlanInterface"),
     path('updateVlanInterface/<int:id_interface>', views.update_vlan_interface, name="updateVlanInterface"),
     path('deleteVlanInterface/<int:id_interface>', views.delete_vlan_interface, name="updateVlanInterface"),
     
     
     
     
 
]