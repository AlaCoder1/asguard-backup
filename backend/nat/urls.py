from django.urls import path
from . import views

urlpatterns = [
    # urls for IPsec configurations
    path('getAllSNat', views.get_all_snat, name="getAllSNat"),
    path('getSNat/<int:id>', views.get_snat, name="getSNat"),
    path('createSNat', views.create_snat, name="v"),
    path('deleteSNat/<int:id>', views.delete_snat, name="deleteSNat"),
    path('updateSNat/<int:id>', views.update_snat, name="updateSNat"),
    path('startSNat/<int:id>', views.start_snat, name="startSNat"),
    path('stopSNat/<int:id>', views.stop_snat, name="stopSNat"),
]
