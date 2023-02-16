from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('<int:id>', views.Settings, name="Settings"),
    path('getSystem/<int:id>', views.getSystem, name="getSystem"),
    path('getNetwork/<int:id>', views.getNetwork, name="getNetwork"),
    path('getServerReseau/<int:id>', views.getServerReseau, name="getServerReseau"),
    path('createSystem', views.createSystem, name="createSystem"),
    path('createServerReseau', views.createServerReseau, name="createServer"),
    path('createNetwork', views.createNetwork, name="createNetwork"),
    # path('deleteServer/<int:id>', views.deleteServer, name="deleteServer"),
    # path('modifyServer/<int:id>', views.modifyServer, name="modifyServer"),
]
