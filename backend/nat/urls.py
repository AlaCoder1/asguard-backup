from django.urls import path
from . import views

urlpatterns = [
    # urls for SNAT
    path('getAllSNat', views.get_all_snat, name="getAllSNat"),
    path('getSNat/<int:id>', views.get_snat, name="getSNat"),
    path('createSNat', views.create_snat, name="v"),
    path('deleteSNat/<int:id>', views.delete_snat, name="deleteSNat"),
    path('updateSNat/<int:id>', views.update_snat, name="updateSNat"),
    path('startSNat/<int:id>', views.start_snat, name="startSNat"),
    path('stopSNat/<int:id>', views.stop_snat, name="stopSNat"),
    
    # urls for DNAT
    path('getAllDNat', views.get_all_dnat, name="getAllDNat"),
    path('getDNat/<int:id>', views.get_dnat, name="getDNat"),
    path('createDNat', views.create_dnat, name="createDNat"),
    path('deleteDNat/<int:id>', views.delete_dnat, name="deleteDNat"),
    path('updateDNat/<int:id>', views.update_dnat, name="updateDNat"),
    path('startDNat/<int:id>', views.start_dnat, name="startDNat"),
    path('stopDNat/<int:id>', views.stop_dnat, name="stopDNat"),
]
