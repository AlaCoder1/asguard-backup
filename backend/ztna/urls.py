from django.urls import path

from . import views

urlpatterns = [
    path('get_Zt_Token', views.get_Zt_Token, name="get_Zt_Token"),
    path('status_ztna', views.status_ztna, name="status_ztna"),
    path('start_ztna', views.start_ztna, name="start_ztna"),
    path('stop_ztna', views.stop_ztna, name="stop_ztna"),

    ########## Identities Paths ##########
    path('get_identities', views.get_all_identities, name='get_identities'),
    path('add_identities', views.add_identities, name='add_identities'),
    path('delete_identities/<str:id>', views.delete_identities, name='delete_identities'),
    path('update_identities/<str:id>', views.update_identities, name='update_identities'),
    path('add_enrollments', views.add_enrollments, name='add_enrollments'),
    path('delete_enrollments/<str:id>', views.delete_enrollments, name='delete_enrollments'),
    
    ########## Routers Paths ##########
    path('get_routers', views.get_all_routers, name='get_routers'),
    path('add_routers', views.add_routers, name='add_routers'),
    path('delete_routers/<str:id>', views.delete_routers, name='delete_routers'),
    path('update_routers/<str:id>', views.update_routers, name='update_routers'),
    path('start_routers/<str:id>', views.start_routers, name='start_routers'),
    path('stop_routers/<str:id>', views.stop_routers, name='stop_routers'),
    
    ########## Config Paths ##########
    path('get_host_configs', views.get_host_configs, name='get_host_configs'),
    path('get_intercept_configs', views.get_intercept_configs, name='get_intercept_configs'),
    path('add_config', views.add_configs, name='add_config'),
    path('delete_config/<str:id>', views.delete_configs, name='delete_config'),
    path('update_config/<str:id>', views.update_configs, name='update_config'),
    
    ########## Services Paths ##########
    path('get_services', views.get_all_services, name='get_services'),
    path('add_services', views.add_services, name='add_services'),
    path('delete_services/<str:id>', views.delete_services, name='delete_services'),
    path('update_services/<str:id>', views.update_services, name='update_services'),
    
    ########## Terminators Paths ##########
    path('get_terminators', views.get_all_terminators, name='get_terminators'),
    path('add_terminators', views.add_terminators, name='add_terminators'),
    path('delete_terminators/<str:id>', views.delete_terminators, name='delete_terminators'),
    path('update_terminators/<str:id>', views.update_terminators, name='update_terminators'),
    
    ########## Policies Paths ##########
    # Edge routers policies
    path('get_all_edge_routers_policies', views.get_all_edge_routers_policies, name='get_all_edge_routers_policies'),
    path('add_edge_routers_policies', views.add_edge_routers_policies, name='add_edge_routers_policies'),
    path('delete_edge_routers_policies/<str:id>', views.delete_edge_routers_policies, name='delete_edge_routers_policies'),
    path('update_edge_routers_policies/<str:id>', views.update_edge_routers_policies, name='update_edge_routers_policies'),
    # Services policies
    path('get_all_services_policies', views.get_all_services_policies, name='get_all_services_policies'),
    path('add_services_policies', views.add_services_policies, name='add_services_policies'),
    path('delete_services_policies/<str:id>', views.delete_services_policies, name='delete_services_policies'),
    path('update_services_policies/<str:id>', views.update_services_policies, name='update_services_policies'),
    # Services Edge routers policies
    path('get_all_services_edge_routers_policies', views.get_all_services_edge_routers_policies, name='get_all_services_edge_routers_policies'),
    path('add_services_edge_routers_policies', views.add_services_edge_routers_policies, name='add_services_edge_routers_policies'),
    path('delete_services_edge_routers_policies/<str:id>', views.delete_services_edge_routers_policies, name='delete_services_edge_routers_policies'),
    path('update_services_edge_routers_policies/<str:id>', views.update_services_edge_routers_policies, name='update_services_edge_routers_policies'),
]
