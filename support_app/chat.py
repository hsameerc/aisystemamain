from channels.generic.websocket import AsyncWebsocketConsumer
import json


class Chat(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            data = json.loads(text_data)
            message = data.get("message", "")

            await self.send(text_data=json.dumps({
                "reply": f"Echo: {message}"
            }))
