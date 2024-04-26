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
]
