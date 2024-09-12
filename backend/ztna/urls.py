from django.urls import path

from . import views

urlpatterns = [
    path('get_Zt_Token', views.get_Zt_Token, name="get_Zt_Token"),

    ########## Identities Paths ##########
    path('get_identities', views.get_all_identities, name='get_identities'),
    path('add_identities', views.add_identities, name='add_identities'),
    path('delete_identities/<int:id>', views.delete_identities, name='delete_identities'),
    path('update_identities/<int:id>', views.update_identities, name='update_identities'),
    
    ########## Routers Paths ##########
    path('get_routers/', views.get_all_routers, name='get_routers'),
    path('add_routers', views.add_routers, name='add_routers'),
    path('delete_routers/<int:id>', views.delete_routers, name='delete_routers'),
    path('update_routers/<int:id>', views.update_routers, name='update_routers'),
    
    ########## Config Paths ##########
    path('get_configs/', views.get_all_configs, name='get_configs'),
    path('add_config', views.add_configs, name='add_config'),
    path('delete_config/<int:id>', views.delete_configs, name='delete_config'),
    path('update_config/<int:id>', views.update_configs, name='update_config'),
    
    ########## Services Paths ##########
    path('get_services/', views.get_all_services, name='get_services'),
    path('add_services', views.add_services, name='add_services'),
    path('delete_services/<int:id>', views.delete_services, name='delete_services'),
    path('update_services/<int:id>', views.update_services, name='update_services'),
    
    ########## Terminators Paths ##########
    path('get_terminators/', views.get_all_terminators, name='get_terminators'),
    path('add_terminators', views.add_terminators, name='add_terminators'),
    path('delete_terminators/<int:id>', views.delete_terminators, name='delete_terminators'),
    path('update_terminators/<int:id>', views.update_terminators, name='update_terminators'),
    
    ########## Policies Paths ##########
    # path('get_edge_router_policies/', views.get_all_edge_router_policies, name='get_edge_router_policies'),
    # path('get_service_policies/', views.get_all_service_policies, name='get_service_policies'),
    # path('get_service_edge_router_policies/', views.get_all_service_edge_router_policies, name='get_service_edge_router_policies'),
]
