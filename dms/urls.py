"""dms URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from views.views import *


urlpatterns = [
    # path('admin/', admin.site.urls),

    path('', login ),
    path('dashboard/', index_page),
    path('userCertifMang/', user_certificate_managment_page),
    path('lan/', lan_page),
    path('firewall/rules', firewall_page),
    path('settings/', settings_page),
    path('openvpn/', openvpn_page),
    path('', include('tasks.urls')),
    path('auth/', include('authentification.urls')),
    path('network/', include('network.urls')),
    path('subscription/', include('subscription.urls')),
    path('users/', include('managementUsers.urls')),
    path('groups/', include('managementGroup.urls')),
    path('servers/', include('managementServers.urls')),
    path('settings/', include('settings.urls')),
    path('api/', include('rest_framework.urls')),
    path('openvpn/', include('openvpn.urls')),
    path('ipsec/', include('ipsec.urls')),
    path('rules/', include('rules.urls')),
    path('openvpn/', include('openvpn.urls')),
    path('gateway/', include('gateway.urls'))
]
