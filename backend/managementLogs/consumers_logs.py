import asyncio
import logging
import subprocess
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from backend.managementLogs.functions import get_attributes_logs
from backend.managementLogs.models import LogsData
from backend.managementLogs.serializers import LogsDataSerializer
from django.db.models import Q

logger = logging.getLogger(__name__) 
class LogsdConsumer(AsyncWebsocketConsumer):
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
        logs_erializer = LogsDataSerializer(data=data)
        if logs_erializer.is_valid() and LogsData.objects.filter(Q(date=data['date'])& Q(date=data['process']) & Q(date=data['message'])) :
            count = LogsData.objects.count()
            if count >= 10000:
                min_timestamp_record = LogsData.objects.order_by('id').first()
                if min_timestamp_record:
                    min_timestamp_record.delete()
            logs_erializer.save()
       
    async def start_data_loop_global_chart(self):
        try:
            while True:
                list_data=[]
                command = "sudo journalctl -n 1000"
                completed_process = subprocess.run(command, shell=True, capture_output=True, text=True)
                output = completed_process.stdout.splitlines()
                for x in output:
                    date, process, message=get_attributes_logs(x)
                    if date is not None and process is not None and message is not None:
                        data = {
                            "date": date,
                            "process": process,
                            "message": message,
                        }
                        # print(data)
                        list_data.append(data)
                        await self.save_system_usage(data)
                        await self.send(json.dumps(list_data))
                await asyncio.sleep(900)
        except asyncio.CancelledError:
            pass