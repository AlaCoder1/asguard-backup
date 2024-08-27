from django.urls import path
from . import views

 
urlpatterns = [
    path('getLogs', views.get_logs_data, name='getLogs'),
    path('downloadLogs', views.download_logs_data, name='downloadLogs'),
    
]