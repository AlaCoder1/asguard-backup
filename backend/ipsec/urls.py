from django.urls import path
from . import views

urlpatterns = [
    path('getAllServerIPsec', views.getAllServerIPsec, name="getAllIPsec"),
    path('getServerIPsec/<int:id>', views.getServerIPsec, name="getServerIPsec"),
    path('createServerIPsec', views.createServerIPsec, name="createServerIPsec"),
    path('deleteServerIPsec/<int:id>', views.deleteServerIPsec, name="deleteServerIPsec"),
    path('updateServerIPsec/<int:id>', views.updateServerIPsec, name="updateServerIPsec"),
    path('statusServerIPsec/<int:id>', views.statusServerIPsec, name="statusServerIPsec"),
    path('statusIPsec', views.statusIPsec, name="statusIPsec"),
]
