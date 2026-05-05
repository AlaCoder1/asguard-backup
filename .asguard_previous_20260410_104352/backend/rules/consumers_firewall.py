import asyncio
import logging
import subprocess
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from backend.rules.functions_logs import get_log_info
from backend.rules.models import FirewallLog
from backend.rules.serializers import FirewallLogsSerializer

logger = logging.getLogger(__name__) 
class FirewallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.info('WebSocket connection established')
        await self.accept()
        await self.channel_layer.group_add(
            "chart_group_global",
            self.channel_name,
        )
        asyncio.create_task(self.start_data_loop_global_chart())

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            "chart_group_global",
            self.channel_name
        )
        logger.info('WebSocket connection for Global Chart closed with code: %s', close_code)
    
    ##function to save in database asynchrononsly
    @database_sync_to_async
    def save_system_usage(self, data):
        """"
        function to save logs in database 
        """
        logs_erializer = FirewallLogsSerializer(data=data)
        if logs_erializer.is_valid() and FirewallLog.objects.filter(log=data['log']) :
            count = FirewallLog.objects.count()
            if count >= 10000:
                min_timestamp_record = FirewallLog.objects.order_by('id').first()
                if min_timestamp_record:
                    min_timestamp_record.delete()
            logs_erializer.save()
       
    async def start_data_loop_global_chart(self):
        while True:
            file="/var/log/nftables/nftables.log"
            data=get_log_info(file)
            await self.save_system_usage(data)
            await self.send(json.dumps(data))
            await asyncio.sleep(900)