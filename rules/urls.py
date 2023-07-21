from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
     path('GetAllRules', views.GetAllRules, name="GetAllRules"),
     path('addRule/<int:id>', views.addRule, name="addRule"),
     path('deleteRule/<int:id>', views.deleteRule, name="deleteRule"),
     path('updateRule/<int:id>', views.updateRule, name="updateRule"),
     path('GetRulesByInterface/<int:id>', views.GetRulesByInterface, name="GetRulesByInterface"),
     
     
     
    

]