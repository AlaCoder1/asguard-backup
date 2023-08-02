from django.contrib import admin
from django.urls import path
from . import views1
from . import views

urlpatterns = [
     path('conf/<str:name_interface>/<int:id>', views1.conf, name="conf"),
    # path('addInterface', views.add_interface, name="addInterface"),
    path('conf/<int:id>', views.conf, name="conf"),
    path('addInterface', views.add_interface, name="addInterface"),
    path('deleteInterface/<int:id>', views.delete_interface, name="deleteInterface"),
    

]
