import asyncio
import json
import websockets
import random


async def hello():
    uri = "ws://localhost:8080"
    rand_user_id = random.randint(0, 99)
    good = random.randint(0, 99) > 20
    async with websockets.connect(uri) as websocket:
        message = {
            'action': 'login',
            'data': {
                'user_id': rand_user_id,
                'token': f'token_{rand_user_id}' if good else 'wrong_token'
            }
        }
        await websocket.send(json.dumps(message))

        async for message in websocket:
            print(json.loads(message))

asyncio.get_event_loop().run_until_complete(hello())
