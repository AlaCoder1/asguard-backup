
from rest_framework import serializers
from backend.openvpn_monitoring.models import VpnMonitoring, VpnMonitoringClient


class VpnMonitoringSerializer(serializers.ModelSerializer):
    class Meta:
            model = VpnMonitoring
            fields = '__all__'
            
class VpnMonitoringClientSerializer(serializers.ModelSerializer):
    vpnmonitor = serializers.PrimaryKeyRelatedField(queryset=VpnMonitoring.objects.all())
    class Meta:
            model = VpnMonitoringClient
            fields = ['username','login_time','address','bytes_recv',
                      'bytes_sent','total_traffic','location','traffic_distr',
                      'vpnmonitor'
                      ]
            
