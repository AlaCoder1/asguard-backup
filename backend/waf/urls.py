from django.urls import path
from . import views

urlpatterns = [
    # Paths for WAF configuration
    path('getConfigWaf', views.get_waf_config, name="getConfigWaf"),
    path('updateConfigWaf/<int:id>', views.update_config_waf, name="updateConfigWaf"),

    # Paths for WAF rules
    path('getAllRuleWaf', views.get_all_waf_rule, name="getAllRuleWaf"),
    path('getRuleWaf/<int:id>', views.get_waf_rule, name="getRuleWaf"),
    path('createRuleWaf', views.create_waf_rule, name="createRuleWaf"),
    path('deleteRuleWaf/<int:id>', views.delete_waf_rule, name="deleteRuleWaf"),
    path('updateRuleWaf/<int:id>', views.update_waf_rule, name="updateRuleWaf"),

    # Paths for WAF applications
    path('getAllApplicationWaf', views.get_all_waf_application, name="getAllApplicationWaf"),
    path('getApplicationWaf/<int:id>', views.get_waf_application, name="getApplicationWaf"),
    path('createApplicationWaf', views.create_waf_application, name="createApplicationWaf"),
    path('deleteApplicationWaf/<int:id>', views.delete_waf_application, name="deleteApplicationWaf"),
    path('updateApplicationWaf/<int:id>', views.update_waf_application, name="updateApplicationWaf"),
    path('restartNginx', views.restart_nginx, name="restartNginx"),

    # Paths for WAF alerts
    path('getAlertsWaf', views.get_all_waf_alerts, name="getAlertsWaf"),
]
