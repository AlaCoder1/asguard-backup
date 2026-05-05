from django.urls import path
from . import views

 
urlpatterns = [
    path('getLogs', views.get_logs_data, name='getLogs'),
    path('downloadLogs', views.download_logs_data, name='downloadLogs'),
    path('getLogrotateByService/<str:service>', views.get_logrotate_by_service, name='getLogrotateByService'),
    path('getLogrotate', views.get_logrotate_data, name='getLogrotate'),
    path('downloadLogrotate', views.download_logrotate_data, name='downloadLogrotate'),
    path('deleteLogrotate/<int:file_id>', views.delete_logrotate_file, name='delete_logrotate_file'),
]