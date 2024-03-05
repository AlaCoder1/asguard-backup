from django.urls import path
from . import views

urlpatterns = [
     path('addVlan', views.add_vlan, name="addVlan"),
     path('updateVlan/<int:id>', views.update_vlan, name="updateVlan"),
     path('deleteVlan/<int:id>', views.delete_vlan, name="deleteVlan"),
     path('deleteVlan/<int:id>', views.delete_vlan, name="deleteVlan"),
     path('getAllVlan', views.get_vlan, name="getAllVlan"),
     path('assignVlanInterface', views.assign_vlan_interface, name="assignVlanInterface"),
     
     
     
     
 
]