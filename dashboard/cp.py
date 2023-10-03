import psutil
import time

def get_cpu_memory_data():
    cpu_percent = psutil.cpu_percent(interval=1)
    memory_percent = psutil.virtual_memory().percent
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print({"cpu_percent":cpu_percent,"memory_percent":memory_percent,"timestamp":timestamp})
    return {
        'cpu_percent': cpu_percent,
        'memory_percent': memory_percent,
        'timestamp': timestamp,
    }
# get_cpu_memory_data()
import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer

class RealTimeDataConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

        while True:
            data = get_cpu_memory_data()
            print(json.dumps(data)) 
            await self.send(json.dumps(data))
            await asyncio.sleep(5)