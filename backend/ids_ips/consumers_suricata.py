import asyncio
import logging
import subprocess
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from backend.ids_ips.models import SuricataLogs
from backend.ids_ips.serializers import SuricataLogsSerializer

logger = logging.getLogger(__name__) 
class LogsSuricataConsumer(AsyncWebsocketConsumer):
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
    
    @database_sync_to_async
    def save_system_usage(self, data):
        """"
        function to save logs in database 
        """
        logs_erializer = SuricataLogsSerializer(data=data)
        if logs_erializer.is_valid() :
            count = SuricataLogs.objects.count()
            if count >= 10000:
                min_timestamp_record = SuricataLogs.objects.order_by('id').first()
                if min_timestamp_record:
                    min_timestamp_record.delete()
            logs_erializer.save()
       
    async def start_data_loop_global_chart(self):
        while True:
            list_data=[]
            command = "sudo cat /var/log/suricata/suricata.log"
            completed_process = subprocess.run(command, shell=True, capture_output=True, text=True)
            output = completed_process.stdout.splitlines()
            for x in output:
                    data = {
                        "log": x,
                    }
                    # print(data)
                    list_data.append(data)
                    await self.save_system_usage(data)
                    await self.send(json.dumps(list_data))
            await asyncio.sleep(900)