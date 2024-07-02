import asyncio
import logging
from random import randint
import subprocess
import time
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from backend.dashboard.models import MonitoringData
from backend.dashboard.serializers import MonitoringDataSerializer
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__) 
class DashboardConsumer(AsyncWebsocketConsumer):
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
    # Create a serializer instance
        Dashboardserializer = MonitoringDataSerializer(data=data)
        # Check if the data is valid
        if Dashboardserializer.is_valid():
            # Check the count of existing entries
            count = MonitoringData.objects.count()
            # If the count exceeds 20, delete the oldest entry
            if count >= 20:
                # Find the record with the minimum timestamp and delete it
                min_timestamp_record = MonitoringData.objects.order_by('timestamp').first()
                if min_timestamp_record:
                    min_timestamp_record.delete()
            # Save the new data
            Dashboardserializer.save()
       
    async def start_data_loop_global_chart(self):
        while True:
            # Execute the command to monitor CPU and memory usage
            command = "sudo top -bn1 | grep \"%Cpu(s)\" | awk '{print $2}' && free | awk '/Mem/{printf \"%.2f\", $4/$2*100}'"
            completed_process = subprocess.run(command, shell=True, capture_output=True, text=True)
            output = completed_process.stdout.splitlines()
            # Parse the output
            cpu_percentage, memory_percentage = map(float, output)
            # Get the current timestamp
            current_time = time.strftime("%Y-%m-%d %H:%M:%S")
            # Convert the formatted timestamp to a Unix timestamp
            unix_timestamp = int(time.mktime(time.strptime(current_time, "%Y-%m-%d %H:%M:%S")))
            ###uptime & current date
            ###uptime
            cmd_uptime="sudo echo \"$(uptime | awk '{{print $1}}') $(uptime | awk -F 'load average: ' '{{print $2}}')\""
            completed_process_uptime=subprocess.run(cmd_uptime, shell=True, capture_output=True, text=True)
            uptime=completed_process_uptime.stdout.strip('\n').strip()
            ###current date
            cmd_date="sudo date"
            completed_process_date=subprocess.run(cmd_date, shell=True, capture_output=True, text=True)
            current_date=completed_process_date.stdout.strip('\n').strip()
            # Create a JSON object with the data
            data = {
                "timestamp": unix_timestamp,
                "cpu_percentage": cpu_percentage,
                "memory_percentage": memory_percentage,
                "uptime":uptime,
                "current_date":current_date
            }
           # Save the data to the database asynchronously
            await self.save_system_usage(data)
            # Send the JSON data to the WebSocket client
            await self.send(json.dumps(data))
            # await self.delete_data()
            
            # Sleep for a while before sending the next data (adjust the interval as needed)
            await asyncio.sleep(1)