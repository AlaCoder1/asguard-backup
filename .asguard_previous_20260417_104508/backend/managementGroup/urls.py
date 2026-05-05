from django.urls import path
from . import views

urlpatterns = [
    path('getAllGroups', views.getAllGroups, name="getAllGroups"),
    path('getGroup/<int:id>', views.getGroup, name="getGroup"),
    path('createGroup', views.createGroup, name="createGroup"),
    path('deleteGroup/<int:id>', views.deleteGroup, name="deleteGroup"),
    path('groupChangeGroupname/<int:id>',
         views.changeGroupname, name="groupChangeGroupname"),
]
