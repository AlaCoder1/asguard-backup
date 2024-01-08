from django.urls import path
from . import views

urlpatterns = [
    path('getAllServerIPsec', views.get_all_server_ipsec, name="getAllIPsec"),
    path('getServerIPsec/<int:id>', views.get_server_ipsec, name="getServerIPsec"),
    path('createServerIPsec', views.create_server_ipsec, name="createServerIPsec"),
    path('deleteServerIPsec/<int:id>', views.delete_server_ipsec, name="deleteServerIPsec"),
    path('updateServerIPsec/<int:id>', views.update_server_ipsec, name="updateServerIPsec"),
    path('statusServerIPsec/<int:id>', views.status_server_ipsec, name="statusServerIPsec"),
    path('statusIPsec', views.status_ipsec, name="statusIPsec"),
]
