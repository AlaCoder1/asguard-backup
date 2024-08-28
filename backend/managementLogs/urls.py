from django.urls import path
from . import views

 
urlpatterns = [
    path('getLogs', views.get_logs_data, name='getLogs'),
    path('downloadLogs', views.download_logs_data, name='downloadLogs'),
    path('getLogrotateByService', views.get_logrotate_by_service, name='getLogrotateByService'),
    path('getLogrotate', views.get_logrotate_data, name='getLogrotate'),
    
]