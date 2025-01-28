from django.urls import path

from . import views, views_configurations, views_identities, views_policies, views_routers, views_services

urlpatterns = [
    path('get_ztna_token', views.get_ztna_token, name="get_ztna_token"),
    path('status_ztna', views.status_ztna, name="status_ztna"),
    path('start_ztna', views.start_ztna, name="start_ztna"),
    path('stop_ztna', views.stop_ztna, name="stop_ztna"),

    ########## Identities Paths ##########
    path('get_identities', views_identities.get_all_identities, name='get_identities'),
    path('add_identities', views_identities.add_identities, name='add_identities'),
    path('delete_identities/<int:id>', views_identities.delete_identities, name='delete_identities'),
    path('update_identities/<int:id>', views_identities.update_identities, name='update_identities'),
    path('add_enrollments', views_identities.add_enrollments, name='add_enrollments'),
    path('get_local_domain_linux/', views.get_local_domain_linux, name='get_local_domain_linux'),
    path('get_local_domain_windows/', views.get_local_domain_windows, name='get_local_domain_windows'),
    
    ########## Routers Paths ##########
    path('get_routers', views_routers.get_all_routers, name='get_routers'),
    path('add_routers', views_routers.add_routers, name='add_routers'),
    path('delete_routers/<int:id>', views_routers.delete_routers, name='delete_routers'),
    path('update_routers/<int:id>', views_routers.update_routers, name='update_routers'),
    path('start_routers/<int:id>', views_routers.start_routers, name='start_routers'),
    path('stop_routers/<int:id>', views_routers.stop_routers, name='stop_routers'),
    
    ########## Config Paths ##########
    path('get_host_configs', views_configurations.get_host_configs, name='get_host_configs'),
    path('get_intercept_configs', views_configurations.get_intercept_configs, name='get_intercept_configs'),
    path('add_config', views_configurations.add_configs, name='add_config'),
    path('delete_intercept_config/<int:id>', views_configurations.delete_intercept_configs, name='delete_intercept_config'),
    path('delete_host_config/<int:id>', views_configurations.delete_host_configs, name='delete_host_config'),
    path('update_intercept_config/<str:id>', views_configurations.update_intercept_configs, name='update_intercept_config'),
    path('update_host_config/<int:id>', views_configurations.update_host_configs, name='update_host_config'),
    
    ########## Services Paths ##########
    path('get_services', views_services.get_all_services, name='get_services'),
    path('add_services', views_services.add_services, name='add_services'),
    path('delete_services/<int:id>', views_services.delete_services, name='delete_services'),
    path('update_services/<int:id>', views_services.update_services, name='update_services'),
    
    ########## Policies Paths ##########
    # Edge routers policies
    path('get_edge_routers_policies', views_policies.get_edge_routers_policies, name='get_edge_routers_policies'),
    path('add_edge_routers_policies', views_policies.add_edge_routers_policies, name='add_edge_routers_policies'),
    path('delete_edge_routers_policies/<int:id>', views_policies.delete_edge_routers_policies, name='delete_edge_routers_policies'),
    path('update_edge_routers_policies/<int:id>', views_policies.update_edge_routers_policies, name='update_edge_routers_policies'),
    # Services policies
    path('get_services_policies', views_policies.get_services_policies, name='get_services_policies'),
    path('add_services_policies', views_policies.add_services_policies, name='add_services_policies'),
    path('delete_services_policies/<int:id>', views_policies.delete_services_policies, name='delete_services_policies'),
    path('update_services_policies/<int:id>', views_policies.update_services_policies, name='update_services_policies'),
    # Services Edge routers policies
    path('get_services_edge_routers_policies', views_policies.get_services_edge_routers_policies, name='get_services_edge_routers_policies'),
    path('add_services_edge_routers_policies', views_policies.add_services_edge_routers_policies, name='add_services_edge_routers_policies'),
    path('delete_services_edge_routers_policies/<int:id>', views_policies.delete_services_edge_routers_policies, name='delete_services_edge_routers_policies'),
    path('update_services_edge_routers_policies/<int:id>', views_policies.update_services_edge_routers_policies, name='update_services_edge_routers_policies'),
]
