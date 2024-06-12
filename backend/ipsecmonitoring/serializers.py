from rest_framework import serializers

from backend.ipsec.models import ServerIPsec
from backend.ipsecmonitoring.models import IpsecMonitoring



class IpsecnMonitoringSerializer(serializers.ModelSerializer):
    tunnel = serializers.PrimaryKeyRelatedField(queryset=ServerIPsec.objects.all())
    class Meta:
                model = IpsecMonitoring
                fields = [
                    "establishetd_date",
                    "active_sessions",
                    "availability",
                    "bytes_in",
                    "bytes_out",
                    "total_bytes",
                    "availability_bytes",
                    "packet_loss",
                    "timestamp",
                    "time_added",
                    "tunnel",
                    
                
            ]
       