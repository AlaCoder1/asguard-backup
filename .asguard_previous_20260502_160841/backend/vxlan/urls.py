from django.urls import path
from . import views

urlpatterns = [
      
      path('getAllVxlan', views.get_vxlan, name="getAllvxlan"),
      path('getvxlaninterface', views.get_vxlan_interface, name="get_vxlan_interface"),
      path('addVxlan', views.add_vxlan, name="addvxlan"),
      path('updateVxlan/<int:id>', views.update_vxlan, name="updateVxlan"),
      path('deleteVxlan/<int:id>', views.delete_vxlan, name="deleteVxlan"),
      path('assignVxlanInterface', views.assign_vxlan_interface, name="assignVxlanInterface"),
      # path('updateVxlanInterface/<int:id_interface>', views.update_vxlan_interface, name="updateVxlanInterface"),
      path('deleteVxlanInterface/<int:id_interface>', views.delete_vxlan_interface, name="deleteVxlanInterface"),
    
]