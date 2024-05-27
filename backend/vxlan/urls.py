from django.urls import path
from . import views

urlpatterns = [
      
      path('getAllVxlan', views.get_vxlan, name="getAllvxlan"),
      path('addVxlan', views.add_vxlan, name="addvxlan"),
      path('assignVxlanInterface', views.assign_vxlan_interface, name="assignVxlanInterface"),
    
]