from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
     path('GetAllRules', views.GetAllRules, name="GetAllRules"),
     path('deleteRule/<int:id>', views.deleteRule, name="deleteRule"),
     path('saveRules/<str:name_interface>', views.saveRules, name="saveRules"),
     path('addRule/<str:name_interface>', views.addRule, name="addRule"),
     path('updateRule/<str:name_interface>', views.updateRule, name="updateRule"),
     
     
     
]