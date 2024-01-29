from django.urls import path
from . import views

 
urlpatterns = [
    ##Other
    # path('getSuricataFile', views.getSuricataFile, name="getSuricataFile"),
    # path('update-suricata-status/<int:id>', views.update_suricata_status, name='update-suricata-status'),
    # path('get-suricata-status/<int:id>', views.get_suricata_status, name='get-suricata-status'),
    # path('updateRule/<int:sid>', views.updateRule, name="updateRule"),
    # path('statusRule/<int:sid>', views.update_status_rule, name="statusRule"),
    # path('getRuleStatus/<int:sid>', views.getRuleStatus, name="getRuleStatus"),
    # path('addDefaultRulesToDatabase/<int:id>', views.addDefaultRulesToDatabase, name='addDefaultRulesToDatabase'),
    # path('addGeneralConfig', views.addGeneralConfig, name='addGeneralConfig'),
     ##Other
    ###########config
    path('UpdateGeneralConfig/<int:id>', views.update_suricata_configuration, name='UpdateGeneralConfig'),
    path('get_suricata_configuration/<int:id>', views.get_suricata_configuration, name='get_suricata_configuration'),
    ########### end config
    ###########Rules
    path('activerSuricataUpdate/<int:id>', views.activer_suricata_update, name='activerSuricataUpdate'),
    path('getRulesFromDatabase/<int:num>', views.get_rules_from_database, name='getRulesFromDatabase'),
    path('saveRulesSuricata/<int:id>', views.save_rules_suricata, name="saveRulesSuricata"),
    path('deleteRule/<int:sid>', views.delete_rule, name="deleteRule"),
    ###########End Rules
    ###########Alerts
    path('addalertsToDatabase/<int:id>', views.add_alerts_to_database, name='addalertsToDatabase'),
    path('GetAlertsFromDatabase/<int:num>', views.get_alerts_from_database, name='GetAlertsFromDatabase'),
    ###########End Alerts
    
] 