from django.urls import path
from . import views

urlpatterns = [
    path('getAllOpenvpns', views.getAllOpenvpns, name="getAllOpenvpns"),
    path('updateOpenVPN/<int:id>', views.updateOpenVPN, name="updateOpenVPN"),
]
