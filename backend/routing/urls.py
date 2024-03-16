from django.urls import path
from . import views

urlpatterns = [
    path('getAllRouting', views.get_all_routing, name="getAllRouting"),
    path('getRouting/<int:id>', views.get_routing, name="getRouting"),
    path('getAllGateway', views.get_all_gateway, name="getAllGateway"),
    path('getGateway/<int:id>', views.get_gateway, name="getGateway"),
    path('createRouting', views.create_routing, name="createRouting"),
    path('deleteRouting/<int:id>', views.delete_routing, name="deleteRouting"),
    path('updateRouting/<int:id>', views.update_routing, name="updateRouting"),
]
