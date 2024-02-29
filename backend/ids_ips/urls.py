from django.urls import path
from . import views

 
urlpatterns = [
  
    ###########config
    path('UpdateGeneralConfig/<int:id>', views.update_suricata_configuration, name='UpdateGeneralConfig'),
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