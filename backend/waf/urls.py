from django.urls import path
from . import views

urlpatterns = [
    path('getConfigWaf', views.get_waf_config, name="getConfigWaf"),
    path('updateConfigWaf/<int:id>', views.update_config_waf, name="updateConfigWaf"),
]
