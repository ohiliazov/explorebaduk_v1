import asyncio
import json
import websockets


async def hello():
    uri = "ws://localhost:8080"
    async with websockets.connect(uri) as websocket:
        message = {
            'target': 'user',
            'action': 'login',
            'user_id': 1,
            'token': 'token_1'
        }
        await websocket.send(json.dumps(message))

        async for message in websocket:
            print(message)

asyncio.get_event_loop().run_until_complete(hello())
