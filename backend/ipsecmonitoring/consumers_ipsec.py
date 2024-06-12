import asyncio
import logging
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from backend.ipsec.models import ServerIPsec
from backend.ipsecmonitoring.functions import get_active_session, get_availabile_bytes, get_availability, get_bytes_in, get_bytes_out, get_establishetd_date, get_packet_loss, get_time_established, get_tunnel_ip, get_uptime
from backend.ipsecmonitoring.serializers import IpsecnMonitoringSerializer
from channels.db import database_sync_to_async
from django.utils.translation import gettext_lazy as _



logger = logging.getLogger(__name__)
class IPSECConsumer(AsyncWebsocketConsumer):
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
        time=text_data_json['time']
        while True:
            data =await self.start_data_loop_ipsec(id_server,time)
            await self.send(json.dumps(data))
            await self.save_system_usage(data)
            await asyncio.sleep(60)
 
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            "chart_group_global",
            self.channel_name
        )
        logger.info('WebSocket connection for Global Chart closed with code: %s', close_code)
   
    @database_sync_to_async
    def save_system_usage(self, data):
        ipsec_serializer=IpsecnMonitoringSerializer(data)
        if ipsec_serializer.is_valid():
            ipsec_serializer.save()
   
    @database_sync_to_async  
    def start_data_loop_ipsec(self,id,time):
        """function to get ipsec monitoring info"""
        tunnel_name=ServerIPsec.objects.get(id=id).conn_name
        uptime=get_uptime()
        estab_time=get_time_established()
        availability =get_availability(estab_time,uptime)
        bytes_in=get_bytes_in()
        bytes_out=get_bytes_out()
        availability_bytes=get_availabile_bytes(bytes_in,bytes_out)
        address=get_tunnel_ip(tunnel_name)
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        unix_timestamp = int(time.mktime(time.strptime(current_time, "%Y-%m-%d %H:%M:%S")))
        active_sessions= get_active_session()
        establishetd_date=get_establishetd_date()
        packet_loss=get_packet_loss(address)
        total_bytes=bytes_in+bytes_out
        data={
            "establishetd_date":establishetd_date,
            "active_sessions":active_sessions,
            "availability":availability,
            "bytes_in":bytes_in,
            "bytes_out":bytes_out,
            "total_bytes":total_bytes,
            "availability_bytes":availability_bytes,
            "packet_loss":packet_loss,
            "timestamp":unix_timestamp,
            "tunnel":id,
            }
        # print(data)
        return data
        
