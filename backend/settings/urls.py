from django.urls import path
from . import views

urlpatterns = [
    path('getSystem/<int:id>', views.getSystem, name="getSystem"),
    path('getNetwork/<int:id>', views.getNetwork, name="getNetwork"),
    path('createSystem', views.create_system, name="createSystem"),
    path('updateSettings', views.update_settings, name="updateSettings"),
    path('getSettings',views.get_settings,name="getSettings"),
    path('generale_settings/<int:id>', views.generale_settings, name="generale_settings"),
    path('get_generale_settings/<int:id>', views.get_generale_settings, name="get_generale_settings"),
    path('time_zones', views.time_zones, name="time_zones"),
    path('gatways_information', views.gatways_information, name="gatways_information"),
    path('getLanguage',views.get_language, name='getLanguage'),
    path('restartNginx', views.restart_nginx, name="restartNginx"),
    path('restartUvicorn', views.restart_uvicorn, name="restartUvicorn"),
]
