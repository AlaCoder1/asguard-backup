from django.urls import path
from . import views

urlpatterns = [
    path('allRuleSquid', views.allRuleSquid, name='allRuleSquid'), 
    path('addRuleSquid', views.addRuleSquid, name='addRuleSquid'), 
    path('updateRuleSquid/<int:rule_id>', views.updateRuleSquid, name='updateRuleSquid'), 
    path('deleteRuleSquid/<int:id>', views.deleteRuleSquid, name='deleteRuleSquid'), 
    path('updateStatusRule/<int:id>', views.updateStatusRule, name='updateStatusRule'), 
    
    path('get_generale_info', views.get_generale_info, name='get_generale_info'),#
    path('update_generale_info', views.update_generale_info, name='update_generale_info'),

    path('disable_auth', views.disable_auth, name='disable_auth'),
    path('enable_auth', views.enable_auth, name='enable_auth'),
    path('status_enable_auth', views.status_enable_auth, name='status_enable_auth'),
    path('change_auth_status', views.change_auth_status, name='change_auth_status'),
    
    # path('restart_squid', views.restart_squid, name='restart_squid'),
    
    path('add_user_squid', views.add_user_squid, name='add_user_squid'),#
    path('delete_user_squid/<int:id>', views.delete_user_squid, name='delete_user_squid'),#
    path('all_proxy_users', views.allProxyUsers, name='all_proxy_users'),#
    # path('change_pwd', views.change_pwd, name='change_pwd'),#
    
    
    path('allGroups', views.allGroups, name='allGroups'), 
    path('changeStausGroup', views.changeStausGroup, name='changeStausGroup'), 
    path('readFromFile', views.readFromFile, name='readFromFile'), 
    path('changeStausElementsInGroup', views.changeStausElementsInGroup, name='changeStausElementsInGroup'), 
    path('allACLFilesWithStatusOfAllElements', views.allACLFilesWithStatusOfAllElements, name='allACLFilesWithStatusOfAllElements'), 

    path('restart', views.restart, name='restart'), 
    path('start', views.start, name='start'), 
    path('stop', views.stop, name='stop'), 
    
]
