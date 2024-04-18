
from rest_framework import serializers
from backend.openvpn_monitoring.models import VpnMonitoring, VpnMonitoringClient


class VpnMonitoringSerializer(serializers.ModelSerializer):
    class Meta:
            model = VpnMonitoring
            fields = [
                "address_server",
                "client_active",
                "capacity_server_in",
                "capacity_client_out",
            ]
            
class VpnMonitoringClientSerializer(serializers.ModelSerializer):
    vpnmonitor = serializers.PrimaryKeyRelatedField(queryset=VpnMonitoring.objects.all())
    class Meta:
            model = VpnMonitoringClient
            fields = ['username','login_time','address','bytes_recv',
                      'bytes_sent','total_traffic','location','traffic_distr',
                      'vpnmonitor'
                      ]
            
