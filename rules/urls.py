from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
     path('GetAllRules', views.GetAllRules, name="GetAllRules"),
     path('addRule/<str:name_interface>', views.addRule, name="addRule"),
     path('deleteRule/<int:id>', views.deleteRule, name="deleteRule"),
     path('updateRule/<int:id>', views.updateRule, name="updateRule"),
     path('GetRulesByInterface/<str:name_interface>', views.GetRulesByInterface, name="GetRulesByInterface"),
     path('GetRulesByType/<str:type_rule>', views.GetRulesByType, name="GetRulesByInterface"),
     
     
     
    

]