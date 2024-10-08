import asyncio
import logging
import subprocess
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


from backend.ztna.functions import get_details_directory
from backend.ztna.models import ZtnaRouterLogs
from backend.ztna.serializers import ZtnaRouterLogsSerializer


logger = logging.getLogger(__name__) 
class LogsZTNAConsumer(AsyncWebsocketConsumer):
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
        logs_erializer =ZtnaRouterLogsSerializer(data=data)
        if logs_erializer.is_valid() :
            count = ZtnaRouterLogs.objects.count()
            if count >= 10000:
                min_timestamp_record = ZtnaRouterLogs.objects.order_by('id').first()
                if min_timestamp_record:
                    min_timestamp_record.delete()
            logs_erializer.save()
       
    async def start_data_loop_global_chart(self):
        while True:
            list_data=[]
            
            file_path="/asguard/newdms/backend/ztna/relays_folder/"
            details_dir1=get_details_directory(file_path)
            for dir in details_dir1:
                details_dir2=get_details_directory(file_path+dir)
                for f in details_dir2:
                    if f.endswith(".log"):
                        path=file_path+dir+f
                        command = f"sudo cat {path}"
                        completed_process = subprocess.run(command, shell=True, capture_output=True, text=True)
                        output = completed_process.stdout.splitlines()
                        for x in output:
                                data = {
                                    "log": x,
                                    "file_path":path,
                                }
                                # print(data)
                                list_data.append(data)
                                await self.save_system_usage(data)
                                await self.send(json.dumps(list_data))
                await asyncio.sleep(900)