import asyncio
import logging
import subprocess
import json
import time
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from backend.ids_ips.models import SuricataLogs
from backend.ids_ips.serializers import SuricataLogsSerializer

logger = logging.getLogger(__name__)

# Throttle: send at most one IDS email per 30 minutes
_last_ids_notif_time = 0.0
_IDS_NOTIF_COOLDOWN = 1800


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
        """function to save logs in database"""
        logs_erializer = SuricataLogsSerializer(data=data)
        if logs_erializer.is_valid():
            count = SuricataLogs.objects.count()
            if count >= 10000:
                min_timestamp_record = SuricataLogs.objects.order_by('id').first()
                if min_timestamp_record:
                    min_timestamp_record.delete()
            logs_erializer.save()

    async def start_data_loop_global_chart(self):
        global _last_ids_notif_time
        while True:
            list_data = []
            command = "sudo cat /var/log/suricata/suricata.log"
            completed_process = subprocess.run(command, shell=True, capture_output=True, text=True)
            output = completed_process.stdout.splitlines()
            alert_lines = [x for x in output if "ALERT" in x or "alert" in x.lower()]
            for x in output:
                data = {"log": x}
                list_data.append(data)
                await self.save_system_usage(data)
                await self.send(json.dumps(list_data))

            if alert_lines and (time.monotonic() - _last_ids_notif_time) > _IDS_NOTIF_COOLDOWN:
                _last_ids_notif_time = time.monotonic()
                sample = alert_lines[0][:120] if alert_lines else ""
                loop = asyncio.get_event_loop()

            await asyncio.sleep(900)