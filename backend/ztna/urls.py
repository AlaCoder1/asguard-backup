from django.urls import path
from . import views

urlpatterns = [
    path('get_Zt_Token', views.get_Zt_Token, name="get_Zt_Token"),
    path('get_identities', views.get_identities, name='get_identities'),
    path('add_identities', views.add_identities, name='add_identities'),
    path('get_routers/', views.get_routers, name='get_routers'),
    path('get_configs/', views.get_configs, name='get_configs'),
    path('get_services/', views.get_services, name='get_services'),
    path('get_terminators/', views.get_terminators, name='get_terminators'),
    path('get_edge_router_policies/', views.get_edge_router_policies, name='get_edge_router_policies'),
    path('get_service_policies/', views.get_service_policies, name='get_service_policies'),
    path('get_service_edge_router_policies/', views.get_service_edge_router_policies, name='get_service_edge_router_policies'),
]
