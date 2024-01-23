from django.urls import path
from . import views

urlpatterns = [
    ####### Area ######
    path('getAllArea', views.get_all_area, name="getAllArea"),
    path('getArea/<int:id>', views.get_area, name="getArea"),
    path('createArea', views.create_area, name="createArea"),
    path('deleteArea/<int:id>', views.delete_area, name="deleteArea"),
    path('updateArea/<int:id>', views.update_area, name="updateArea"),
    
    ####### SDWAN Rules ######
    path('getAllSdwanRule', views.get_all_sdwan_rule, name="getAllSdwanRule"),
    path('getSdwanRule/<int:id>', views.get_sdwan_rule, name="getSdwanRule"),
    path('createSdwanRule', views.create_sdwan_rule, name="createSdwanRule"),
    path('deleteSdwanRule/<int:id>', views.delete_sdwan_rule, name="deleteSdwanRule"),
    path('updateSdwanRule/<int:id>', views.update_sdwan_rule, name="updateSdwanRule"),
    path('startSdwanRule/<int:id>', views.start_sdwan_rule, name="startSdwanRule"),
]