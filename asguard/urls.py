"""asguard URL Configuration

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
from backend.dashboard import consumers
from views.views import *
from django.conf.urls import handler404
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
schema_view = get_schema_view(
    openapi.Info(
        title="API ASGUARD FIREWALL",
        default_version='v1',
        description="API ASGUARD FIREWALL",
        terms_of_service="https://www.ourapp.com/policies/terms/",
        contact=openapi.Contact(email="contact@swaggerAsguard.local"),
        license=openapi.License(name="Test License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)



urlpatterns = [
    # path('admin/', admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('', login ),
    path('dashboard/', index_page),
    path('userCertifMang/', user_certificate_managment_page),
    path('interfaces/list-of-interface', interface_page),
    path('system/user-certificat-management', user_certificate_managment_page),
    path('firewall/rules', firewall_page),
    path('settings/', settings_page),
    path('openvpn/', openvpn_page),
    path('', include('backend.tasks.urls')),
    path('auth/', include('backend.authentification.urls')),
    path('network/', include('backend.network.urls')),
    path('subscription/', include('backend.subscription.urls')),
    path('users/', include('backend.managementUsers.urls')),
    path('groups/', include('backend.managementGroup.urls')),
    path('key_pairs/', include('backend.managementKeypairs.urls')),
    path('key_pairs/', keyPair_page),
    path('servers/', include('backend.managementServers.urls')),
    path('certificates/', include('backend.managementCertificates.urls')),
    path('settings/', include('backend.settings.urls')),
    path('api/', include('rest_framework.urls')),
    path('openvpn/', include('backend.openvpn.urls')),
    # path('ipsec/', include('backend.ipsec.urls')),
    path('ipsec/', ipsec_page),
    path('rules/', include('backend.rules.urls')),
    path('gateway/', include('backend.gateway.urls')),
    path("monitoring/",include("backend.dashboard.urls"))
]

# ws/wss url patterns
websocket_urlpatterns = [
    # consumer for a particular user
      path('ws/data/', consumers.DashboardConsumer.as_asgi()),
]

handler404 = 'views.views.error_404_view'