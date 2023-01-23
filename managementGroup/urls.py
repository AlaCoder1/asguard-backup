from django.urls import path
from . import views

urlpatterns = [
    path('createGroup', views.createGroup, name="createGroup"),
    path('getAllGroups', views.getAllGroups, name="getAllGroups"),
    path('deleteGroup', views.deleteGroup, name="deleteGroup"),
    path('groupChangeGroupname', views.change_groupname, name="groupChangeGroupname"),
]
