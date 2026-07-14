import asyncio
import logging
import time
import json
import os
from channels.generic.websocket import AsyncWebsocketConsumer
from backend.dashboard.models import MonitoringData
from backend.dashboard.serializers import MonitoringDataSerializer
from channels.db import database_sync_to_async
import psutil
logger = logging.getLogger(__name__) 
class DashboardConsumer(AsyncWebsocketConsumer):
    _last_saved_at = 0.0
    _save_lock = asyncio.Lock()

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
        try:
            psutil.cpu_percent(interval=None)
            while True:
                cpu_percentage = psutil.cpu_percent(interval=None)
                memory_percentage = psutil.virtual_memory().percent
                # Get the current timestamp
                current_time = time.strftime("%Y-%m-%d %H:%M:%S")
                # Convert the formatted timestamp to a Unix timestamp
                unix_timestamp = int(time.mktime(time.strptime(current_time, "%Y-%m-%d %H:%M:%S")))
                ### uptime & load average
                uptime_seconds = max(0, int(time.time() - psutil.boot_time()))
                uptime_days = uptime_seconds // 86400
                uptime_hours = (uptime_seconds % 86400) // 3600
                uptime_minutes = (uptime_seconds % 3600) // 60
                if uptime_days > 0:
                    uptime = f"{uptime_days}j {uptime_hours}h {uptime_minutes}min"
                elif uptime_hours > 0:
                    uptime = f"{uptime_hours}h {uptime_minutes}min"
                else:
                    uptime = f"{uptime_minutes}min"

                try:
                    load_values = os.getloadavg()
                    load_average = ", ".join(f"{value:.2f}" for value in load_values)
                except (AttributeError, OSError):
                    load_average = ""

                current_date = time.strftime("%a %b %d %H:%M:%S %Y")
                # Create a JSON object with the data
                data = {
                    "timestamp": unix_timestamp,
                    "cpu_percentage": cpu_percentage,
                    "memory_percentage": memory_percentage,
                    "uptime":uptime,
                    "load_average": load_average,
                    "current_date":current_date
                }
                # Keep history useful without writing once per second per open tab.
                now = time.time()
                async with self.__class__._save_lock:
                    if now - self.__class__._last_saved_at >= 5:
                        await self.save_system_usage(data)
                        self.__class__._last_saved_at = now
                # Send the JSON data to the WebSocket client
                   # Send to client
                try:
                    await self.send(json.dumps(data))
                except RuntimeError:
                    break 
                
                # Sleep for a while before sending the next data (adjust the interval as needed)
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass
