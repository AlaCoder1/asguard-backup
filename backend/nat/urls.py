from django.urls import path

from . import views_one_to_one_nat
from . import views_snat
from . import views_dnat

urlpatterns = [
    # urls for SNAT
    path('getAllSNat', views_snat.get_all_snat, name="getAllSNat"),
    path('getSNat/<int:id>', views_snat.get_snat, name="getSNat"),
    path('createSNat', views_snat.create_snat, name="createSNat"),
    path('deleteSNat/<int:id>', views_snat.delete_snat, name="deleteSNat"),
    path('updateSNat/<int:id>', views_snat.update_snat, name="updateSNat"),
    path('startSNat/<int:id>', views_snat.start_snat, name="startSNat"),
    path('stopSNat/<int:id>', views_snat.stop_snat, name="stopSNat"),
    path('changeSNatPosition/<int:id>', views_snat.change_snat_position, name="changeSNatPosition"),
    
    # urls for OneToOne NAT
    path('getAllOneToOneNat', views_one_to_one_nat.get_all_one_to_one_nat, name="getAllOneToOneNat"),
    path('getOneToOneNat/<int:id>', views_one_to_one_nat.get_one_to_one_nat, name="getOneToOneNat"),
    path('createOneToOneNat', views_one_to_one_nat.create_one_to_one_nat, name="createOneToOneNat"),
    path('deleteOneToOneNat/<int:id>', views_one_to_one_nat.delete_one_to_one_nat, name="deleteOneToOneNat"),
    path('updateOneToOneNat/<int:id>', views_one_to_one_nat.update_one_to_one_nat, name="updateOneToOneNat"),
    path('startOneToOneNat/<int:id>', views_one_to_one_nat.start_one_to_one_nat, name="startOneToOneNat"),
    path('stopOneToOneNat/<int:id>', views_one_to_one_nat.stop_one_to_one_nat, name="stopOneToOneNat"),
    path('changeOneToOneNatPosition/<int:id>', views_one_to_one_nat.change_one_to_one_nat_position, name="changeOneToOneNatPosition"),
    
    # urls for DNAT
    path('getAllDNat', views_dnat.get_all_dnat, name="getAllDNat"),
    path('getDNat/<int:id>', views_dnat.get_dnat, name="getDNat"),
    path('createDNat', views_dnat.create_dnat, name="createDNat"),
    path('deleteDNat/<int:id>', views_dnat.delete_dnat, name="deleteDNat"),
    path('updateDNat/<int:id>', views_dnat.update_dnat, name="updateDNat"),
    path('startDNat/<int:id>', views_dnat.start_dnat, name="startDNat"),
    path('stopDNat/<int:id>', views_dnat.stop_dnat, name="stopDNat"),
    path('changeDNatPosition/<int:id>', views_dnat.change_dnat_position, name="changeDNatPosition"),
]
