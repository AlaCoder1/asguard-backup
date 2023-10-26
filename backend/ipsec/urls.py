from django.urls import path
from . import views

urlpatterns = [
    path('getAllIPsec', views.getAllIPsec, name="getAllIPsec"),
]
