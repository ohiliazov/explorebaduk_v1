import asyncio
import json
import websockets


async def hello():
    uri = "ws://localhost:8080"
    logged_in = False
    async with websockets.connect(uri) as websocket:
        message = {
            'target': 'auth',
            'auth_action': 'login',
            'user_id': 1,
            'token': 'token_1'
        }
        await websocket.send(json.dumps(message))

        async for message in websocket:
            print(message)
            data = json.loads(message)
            if not logged_in:
                if data['status'] == 'success':
                    logged_in = True

asyncio.get_event_loop().run_until_complete(hello())
