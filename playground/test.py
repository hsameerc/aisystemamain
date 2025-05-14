import asyncio
import websockets
import json


async def test_websocket():
    uri = "ws://127.0.0.1:8080/ws/chat/"
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({"message": "Hello WebSocket"}))
        response = await websocket.recv()
        print(f"Received: {response}")


asyncio.run(test_websocket())
