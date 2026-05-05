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
from backend.ids_ips import consumers_stats, consumers_suricata
from backend.ipsecmonitoring import consumers_ipsec
from backend.managementLogs import consumers_logs
from backend.openvpn import consumers_logs_vpn
from backend.openvpn_monitoring import consumers_openvpn
from backend.proxy import consumers_logs_access, consumers_logs_cache, consumers_logs_store
from backend.rules import consumers_firewall
from backend.ztna import consumers_logs_controller, consumers_logs_ztna
from views.views import *
from django.conf.urls import handler404
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf.urls.static import static
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
    path('userCertifMang/', user_managment_page),
    path('interfaces/list-of-interface', interface_page),
    path('interfaces/type-of-interface', interface_type),
    path('system/user-management', user_managment_page),
    path('system/certificat-management', certificate_managment_page),
    path('firewall/rules', firewall_page),
    path('openvpn/', openvpn_page),
    path('asguard/license/', subscription_page),
    path('', include('backend.tasks.urls')),
    path('auth/', include('backend.authentification.urls')),
    path('network/', include('backend.network.urls')),
    path('subscription/', include('backend.subscription.urls')),
    path('users/', include('backend.managementUsers.urls')),
    path('groups/', include('backend.managementGroup.urls')),
    path('key_pairs/', include('backend.managementKeypairs.urls')),
    path('key_pairs/', key_pair_page),
    path('servers/', include('backend.managementServers.urls')),
    path('certificates/', include('backend.managementCertificates.urls')),
    path('settings/', include('backend.settings.urls')),
    path('api/', include('rest_framework.urls')),
    path('openvpn/', include('backend.openvpn.urls')),
    path('ipsec/', include('backend.ipsec.urls')),
    path('ipsec/', ipsec_page),
    path('proxy/', squid_proxy),
    path('sdwan/', sdwan_page),
    path('settings/', setting_page),
    path('waf/', waf_page),
    path('sdwan/', include('backend.sdwan.urls')),
    path('rules/', include('backend.rules.urls')),
    path('gateway/', include('backend.gateway.urls')),
    path("monitoring/",include("backend.dashboard.urls")),
    path("ids-ips/",include("backend.ids_ips.urls")),
    path('proxy/', include('backend.proxy.urls')),
    path('nat/', include('backend.nat.urls')),
    path("vlan/", include("backend.vlan.urls")),
    path("waf/", include("backend.waf.urls")),
    path("server_dhcp4/", include("backend.server_dhcp4.urls")),
    path("services/server-dhcp4", server_dhcp4_page),
    path("ztna/", include("backend.ztna.urls")),
    path("ztna/", ztna_page),
    path("ids-ips/", suricata),
    path("firewall/nat/", nat_page),
    path("success/", success),
    path("vpnmonitoring/", openvpn_monitoring),
    path("routing/", routing_page),
    path('ldap/', include('backend.LdapServer.urls')),
    path('routing/', include('backend.routing.urls')),
    path("profile/",profile_page),
    path("vxlan/",include('backend.vxlan.urls')),
    path("system_log/",system_log),
    path("logrotate/",logrotate_page),
    path("double-masque/",double_masque),
    path("system_log/",include('backend.managementLogs.urls')),
    path("double_mask/",include("backend.double_mask.urls")),
    path("backup/",backup_page),

    path('backup/', include('backend.backup.urls'))


]

# ws/wss url patterns
websocket_urlpatterns = [
    # consumer for a particular user
      path('ws/data/', consumers.DashboardConsumer.as_asgi()),
      path('ws/vpnmonitoring/', consumers_openvpn.OpenVpnConsumer.as_asgi()),
      path('ws/ipsecmonitoring/', consumers_ipsec.IPSECConsumer.as_asgi()),
      path('ws/logs/',consumers_logs.LogsdConsumer.as_asgi()),
      path('ws/logs_vpn/',consumers_logs_vpn.LogsVPNConsumer.as_asgi()),
      path('ws/logs_stats/',consumers_stats.LogsStatsConsumer.as_asgi()),
      path('ws/logs_suricata/',consumers_suricata.LogsSuricataConsumer.as_asgi()),
      path('ws/logs_squid_cache/',consumers_logs_cache.LogsCacheConsumer.as_asgi()),
      path('ws/logs_squid_access/',consumers_logs_access.LogsAccessConsumer.as_asgi()),
      path('ws/logs_squid_store/',consumers_logs_store.LogsStoreConsumer.as_asgi()),
      path('ws/logs_ztna_controller/',consumers_logs_controller.LogsControllerConsumer.as_asgi()),
      path('ws/logs_ztna_router/',consumers_logs_ztna.LogsZTNAConsumer.as_asgi()),
      path('ws/firewall_log/',consumers_firewall.FirewallConsumer.as_asgi()),
      
      
      
      
]


handler404 = 'views.views.error_404_view'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)