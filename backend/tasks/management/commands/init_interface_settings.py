from backend.network.serializers import IP4ConfigSerializer, InterfaceSerializer
from backend.network.functions import get_connection_uuid
from backend.settings.utils import execute_command
from django.core.management.base import BaseCommand
from django.db import IntegrityError



class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        try:
            uuid,name=get_connection_uuid(connection_name=None)
            if uuid is not None:
                cmd = f"""
sudo nmcli connection modify {uuid} ipv4.method manual ipv4.addresses '192.168.1.1/24' ipv4.gateway '' ipv4.route-metric '' \
&& sudo nmcli connection down {uuid} \
&& sudo nmcli connection up {uuid}"""
                _,error=execute_command(cmd)
                if not error:
                    interface_data={
                        "ifname":name,
                        "name_interface":"LAN",
                    }
                    interface_serializer=InterfaceSerializer(data=interface_data)
                    if interface_serializer.is_valid():
                        interface_serializer.save()
                        id = interface_serializer.instance.pk
                        data_ip4={
                            "interface":id,
                            "typeip4":"static",
                            "typedhcp":None,
                            "ip_address":"192.168.1.1",
                            "netmask":"24",
                        }
                        ip4_serializer=IP4ConfigSerializer(data=data_ip4 )
                        if ip4_serializer.is_valid():
                            ip4_serializer.save()
                            
                        else:
                            return f"{ip4_serializer.errors}"
                    else:
                        return f"{interface_serializer.errors}"
                else: 
                    return f"{error}"
            else:
                return "You don't have active interface!"        
                
        except IntegrityError as e:
            return "Error: " + str(e)
