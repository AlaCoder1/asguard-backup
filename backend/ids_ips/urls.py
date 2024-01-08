from django.urls import path
from . import views

 
urlpatterns = [
    path('getSuricataFile', views.getSuricataFile, name="getSuricataFile"),
    path('update-suricata-status/<int:id>', views.update_suricata_status, name='update-suricata-status'),
    path('get-suricata-status/<int:id>', views.get_suricata_status, name='get-suricata-status'),
    path('UpdateGeneralConfig/<int:id>', views.update_suricata_configuration, name='UpdateGeneralConfig'),
    path('get_suricata_configuration/<int:id>', views.get_suricata_configuration, name='get_suricata_configuration'),
    # path('updateRule/<int:sid>', views.updateRule, name="updateRule"),
    path('statusRule/<int:sid>', views.update_status_rule, name="statusRule"),
    # path('getRuleStatus/<int:sid>', views.getRuleStatus, name="getRuleStatus"),
    path('deleteRule/<int:sid>', views.deleteRule, name="deleteRule"),
    path('saveRulesSuricata/<int:id>', views.save_rules_suricata, name="saveRulesSuricata"),
    # path('addDefaultRulesToDatabase/<int:id>', views.addDefaultRulesToDatabase, name='addDefaultRulesToDatabase'),
    path('activerSuricataUpdate/<int:id>', views.activerSuricataUpdate, name='activerSuricataUpdate'),
    path('getRulesFromDatabase/<int:num>', views.getRulesFromDatabase, name='getRulesFromDatabase'),
    path('addalertsToDatabase/<int:id>', views.addalertsToDatabase, name='addalertsToDatabase'),
    path('GetAlertsFromDatabase/<int:num>', views.GetAlertsFromDatabase, name='GetAlertsFromDatabase'),
    path('addGeneralConfig', views.addGeneralConfig, name='addGeneralConfig'),
] 