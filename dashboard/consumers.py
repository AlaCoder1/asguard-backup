
from channels.generic.websocket import AsyncWebsocketConsumer
import json
import logging
logger = logging.getLogger(__name__)
class DashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        
        await self.channel_layer.group_discard(
            f"chart_group_{self.server_id}",
            self.channel_name
        )
        logger.info('WebSocket connection closed with code: %s', close_code)

    async def send_chart_data(self, chart_data):
        logger.debug('Sending chart data: %s', chart_data),
        await self.send(json.dumps(chart_data))