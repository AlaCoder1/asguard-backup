from django.contrib import admin
from django.urls import path
from . import views1

urlpatterns = [
     path('conf/<str:name_interface>/<int:id>', views1.conf, name="conf"),
    # path('addInterface', views.add_interface, name="addInterface"),

]
