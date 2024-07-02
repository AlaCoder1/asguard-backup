import asyncio
import logging
import time
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from backend.openvpn.models import ClientOpenvpn, ServerOpenvpn
from channels.db import database_sync_to_async
from backend.openvpn_monitoring.models import VpnMonitoring, VpnMonitoringClient
from backend.openvpn_monitoring.serializers import VpnMonitoringClientSerializer, VpnMonitoringSerializer
from .functions_client import *
import pyshark
from django.core import serializers
from django.contrib.auth.hashers import  check_password
from django.utils.translation import gettext_lazy as _


# Constants
ERROR_MESSAGES_INVALID_PASSWORD = _("Invalid password")
ERROR_MESSAGES_MANAGEMENT = _("Please provide management information!")

logger = logging.getLogger(__name__)
class OpenVpnConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.info('WebSocket connection established')
        await self.accept()
        await self.channel_layer.group_add(
            "chart_group_global",
            self.channel_name,
        )
       
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        id_server = text_data_json['id']
        password=text_data_json['password']
        while True:
            data =await self.start_data_loop_openvpn(id_server,password)
            await self.send(json.dumps(data))
            if not isinstance(data, str):
                await self.save_system_usage(data)
                await asyncio.sleep(60)
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            "chart_group_global",
            self.channel_name
        )
        logger.info('WebSocket connection for Global Chart closed with code: %s', close_code)
   
    #function to save in database asynchrononsly
    @database_sync_to_async
    def save_system_usage(self, data):
        data_server={
           "address_server": data['address_server'] if 'address_server' in data else None,
            "client_active": data['client_active'] if 'client_active' in data else None,
            "capacity_server_in": data['capacity_client_in']['initial_size'] if 'capacity_client_in' in data else None,
            "capacity_client_out": data['capacity_client_out']['initial_size'] if 'capacity_client_out' in data else None

        }
        data_client = [
        {
            "username": d['username'] if 'username' in d else None,
            "login_time": d['login_time'] if 'login_time' in d else None,
            "address": d['address'] if 'address' in d else None,
            "bytes_recv": d['bytes_recv']['initial_size'] if 'bytes_recv' in d else None,
            "bytes_sent": d['bytes_sent']['initial_size'] if 'bytes_sent' in d else None,
            "total_traffic": d['total_traffic']['initial_size'] if 'total_traffic' in d else None,
            "location": d['location'] if 'location' in d else None,
            "traffic_distr": d['traffic_distr'] if 'traffic_distr' in d else None
            }
            for d in data['info_clients']
                        ]
        if not VpnMonitoring.objects.filter(address_server=data_server["address_server"]).exists():
            # Create a serializer instance
            dashboard_serializer = VpnMonitoringSerializer(data=data_server)
        else:
            object_serializer=VpnMonitoring.objects.get(address_server=data_server["address_server"])
            dashboard_serializer = VpnMonitoringSerializer(object_serializer,data=data_server)

        # Check if the data is valid
        if dashboard_serializer.is_valid():
            dashboard_instance = dashboard_serializer.save()
            id_vpn = dashboard_instance.id
            if id_vpn is not None:
                for client in data_client:
                    client['vpnmonitor']=id_vpn
                    client_serializer = VpnMonitoringClientSerializer(data=client)
                    if client_serializer.is_valid():
                        # Check the count of existing entries
                        count = VpnMonitoring.objects.count()
                        # If the count exceeds 20, delete the oldest entry
                        if count >= 20:
                            # Find the record with the minimum timestamp and delete it
                            min_timestamp_record = VpnMonitoring.objects.order_by('timestamp').first()
                            if min_timestamp_record:
                                min_timestamp_record.delete()
                        # Save the new data
                        client_serializer.save()
                         # Check the count of existing entries
                        count2 = VpnMonitoringClient.objects.count()
                        # If the count exceeds 20, delete the oldest entry
                        if count2 >= 20:
                            # Find the record with the minimum timestamp and delete it
                            min_timestamp_record2 = VpnMonitoringClient.objects.order_by('timestamp').first()
                            if min_timestamp_record2:
                                min_timestamp_record2.delete()
        #             else:
        #                 print({"client serializer": client_serializer.errors})
        # else:
        #     print({"dashboard_serializer": dashboard_serializer.errors})

   
    ##function to convert bytes
    def convert_bytes(self,capture_size):
            if capture_size >= 1073741824:
                capture_info={
                "initial_size":capture_size,
                "capture_size":capture_size/(1024*1024*1024),
                "unit":"GB"
                }
            elif capture_size >= 1048576:
                capture_info={
                "initial_size":capture_size,
                "capture_size":capture_size/(1024*1024),
                "unit":"MB"
                }
            elif capture_size >= 1024:
                capture_info={
                "initial_size":capture_size,
                "capture_size":capture_size/1024,
                "unit":"KB"
                }
            else:
                capture_info={
                "initial_size":capture_size,
                "capture_size":capture_size,
                "unit":"Bytes"
                }
            return capture_info
   
    def get_top_traffic(self,info_clients):
        """function to get top traffic """
        top_traffic = sorted(info_clients, key=lambda x: x['total_traffic']['initial_size'])
        top_traffic = [{'username': obj['username'],"total_traffic":obj['total_traffic']} for obj in top_traffic[:10]]
        return top_traffic
   
    def get_top_network(self,info_clients):
        """get network activity"""
        top_traffic = sorted(info_clients, key=lambda x: x['total_traffic']['initial_size'])
        top_traffic = [{'username': obj['username'],"total_traffic":obj['total_traffic']} for obj in top_traffic[:2]]
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        # Convert the formatted timestamp to a Unix timestamp
        unix_timestamp = int(time.mktime(time.strptime(current_time, "%Y-%m-%d %H:%M:%S")))
        if len(top_traffic)!=0:
            if len(top_traffic)>=2:
                top_network={
                    "timestamp": unix_timestamp,
                    "first_network":top_traffic[0]['total_traffic'],
                    "second_network":top_traffic[1]['total_traffic']
                }
            else:
                top_network={
                    "timestamp": unix_timestamp,
                    "first_network":top_traffic[0]['total_traffic'],
                }
        else:
            top_network={
                    "timestamp": unix_timestamp,
                    "first_network":0,
                }
           
        return top_network
   
    def get_top_logging(self,vpn,name_server,address_server):
        """function to get top logging """
        capture = pyshark.LiveCapture(interface=name_server)
          # Execute get openvpn client informations
        traffic_counts={}
        for packet in capture.sniff_continuously(packet_count=1):
            # Extract source and destination IPs
            src_ip = packet.ip.src
            if src_ip!=address_server:
                # Update traffic counts in the dictionary
                key = (src_ip)
                traffic_counts[key] = traffic_counts.get(key, 0) + 1
            # # Print the top traffic
        top_logging = sorted(traffic_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        for i, (src_ip, count) in enumerate(top_logging):
            username=vpn['sessions'][src_ip]['username']
            top_logging[i] = {"username":username,"count":count}
        return top_logging
   
    @database_sync_to_async  
    def start_data_loop_openvpn(self,id,password):
        """function to get top logging """
        vpn_db=ServerOpenvpn.objects.get(pk=id)
        name_server=vpn_db.dev+"_"+vpn_db.name
        all_client=ClientOpenvpn.objects.all().count()
        if vpn_db.client_management_password is not None:
            check_match=check_password(password,  vpn_db.client_management_password)
            if check_match:
                cfg=[{'host': 'localhost', 'port': vpn_db.client_management_port, 'name':name_server, 'password': vpn_db.client_management_password, 'show_disconnect': False,"server_status":vpn_db.server_status} ]
                vpn = OpenvpnMgmtInterface(cfg).vpns
                vpn=vpn[0]
                client_active=vpn['stats']['nclients'] if 'stats' in vpn and 'nclients' in vpn['stats'] else 0
                capacity_server_in=int(vpn['stats']['bytesin'])   if 'stats'in vpn and 'bytesin' in vpn['stats'] else 0
                capacity_server_out=int(vpn['stats']['bytesout'])   if 'stats'in vpn and 'bytesout' in vpn['stats'] else 0
                address_server=str(vpn["state"]["local_ip"]) if "state" in vpn  and "local_ip" in vpn["state"]  else None
                info_clients=[]
                if 'sessions' in vpn:
        
                    info_clients = [
                                    {
                                        "username": session['username'],
                                        "login_time": str(session['connected_since']),
                                        "address": str(session['local_ip']),
                                        "bytes_recv":self.convert_bytes(int(session['bytes_recv'])),
                                        "bytes_sent":self.convert_bytes(int(session['bytes_sent'])),
                                        "total_traffic":self.convert_bytes(int(session['bytes_recv'])+int(session['bytes_sent'])),
                                        "location":session['location'],
                                        "traffic_distr":((int(session['bytes_recv'])+int(session['bytes_sent']))/(capacity_server_in+capacity_server_out))*100
                                    }
                                for session in vpn['sessions'].values()
                                ]
                # Create a JSON object with the data
                data = {
                    "address_server":address_server,
                    "all_client": all_client,
                    "client_active": client_active,
                    "capacity_client_in":self.convert_bytes(capacity_server_in),
                    "capacity_client_out":self.convert_bytes(capacity_server_out),
                    "info_clients":info_clients,
                    "top_traffic":self.get_top_traffic(info_clients),
                    # "top_logging":self.get_top_logging(vpn,name_server,address_server),
                    "top_network":self.get_top_network(info_clients)
                
                }
                return data
            else:
                return f"{ERROR_MESSAGES_INVALID_PASSWORD}"
        else:
            return f"{ERROR_MESSAGES_MANAGEMENT}"
