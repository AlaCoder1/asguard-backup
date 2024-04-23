from django.urls import path
from . import views

urlpatterns = [
    # urls for SNAT
    path('getAllSNat', views.get_all_snat, name="getAllSNat"),
    path('getSNat/<int:id>', views.get_snat, name="getSNat"),
    path('createSNat', views.create_snat, name="createSNat"),
    path('deleteSNat/<int:id>', views.delete_snat, name="deleteSNat"),
    path('updateSNat/<int:id>', views.update_snat, name="updateSNat"),
    path('startSNat/<int:id>', views.start_snat, name="startSNat"),
    path('stopSNat/<int:id>', views.stop_snat, name="stopSNat"),
    path('changeSNatPosition/<int:id>', views.change_snat_position, name="changeSNatPosition"),
    
    # urls for OneToOne NAT
    path('getAllOneToOneNat', views.get_all_one_to_one_nat, name="getAllOneToOneNat"),
    path('getOneToOneNat/<int:id>', views.get_one_to_one_nat, name="getOneToOneNat"),
    path('createOneToOneNat', views.create_one_to_one_nat, name="createOneToOneNat"),
    path('deleteOneToOneNat/<int:id>', views.delete_one_to_one_nat, name="deleteOneToOneNat"),
    path('updateOneToOneNat/<int:id>', views.update_one_to_one_nat, name="updateOneToOneNat"),
    path('startOneToOneNat/<int:id>', views.start_one_to_one_nat, name="startOneToOneNat"),
    path('stopOneToOneNat/<int:id>', views.stop_one_to_one_nat, name="stopOneToOneNat"),
    path('changeOneToOneNatPosition/<int:id>', views.change_one_to_one_nat_position, name="changeOneToOneNatPosition"),
    
    # urls for DNAT
    path('getAllDNat', views.get_all_dnat, name="getAllDNat"),
    path('getDNat/<int:id>', views.get_dnat, name="getDNat"),
    path('createDNat', views.create_dnat, name="createDNat"),
    path('deleteDNat/<int:id>', views.delete_dnat, name="deleteDNat"),
    path('updateDNat/<int:id>', views.update_dnat, name="updateDNat"),
    path('startDNat/<int:id>', views.start_dnat, name="startDNat"),
    path('stopDNat/<int:id>', views.stop_dnat, name="stopDNat"),
    path('changeDNatPosition/<int:id>', views.change_dnat_position, name="changeDNatPosition"),
]
