from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
     # path('GetAllRules', views.GetAllRules, name="GetAllRules"),
     path('deleteRule/<int:id>', views.delete_rule, name="deleteRule"),
     path('addRule/<str:name_interface>', views.add_rule, name="addRule"),
     path('saveRules/<str:name_interface>', views.save_rules, name="saveRules"),
     path('updateRule/<str:name_interface>', views.update_rule, name="updateRule"),
     
     
     
]