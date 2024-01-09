from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
     path('GetConfigurations', views.getconfiguratiosnfromdatabase, name="Get_Configurations"),
     path('updateClamav/<int:id>', views.update_clamav_configuration, name="Update_Configurations"),
     path('Updatefreshclam', views.update_freshclam_database, name="update_freshclam"),
     path('Fullscan',views.clamavscanview,name="full_scan_clamav"),
]
