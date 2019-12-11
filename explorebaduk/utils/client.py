import asyncio
import json
import websockets
import random


async def hello():
    uri = "ws://localhost:8080"
    rand_user_id = random.randint(0, 99)
    async with websockets.connect(uri) as websocket:
        while True:
            message = {
                'type': 'login',
                'data': {
                    'user_id': rand_user_id,
                    'token': f'token_{rand_user_id}' if random.randint(0, 100) < 80 else 'wrong_token'
                }
            }
            await asyncio.sleep(random.random()*10)
            await websocket.send(json.dumps(message))
            await websocket.recv()
            print('login')

            if random.randint(0, 100) > 80:
                await asyncio.sleep(random.random()*10)
                await websocket.send(json.dumps(message))
                await websocket.recv()
                print('re-login')

            message = {'type': 'logout', 'data': ''}
            await asyncio.sleep(random.random()*10)
            await websocket.send(json.dumps(message))
            await websocket.recv()
            print('logout')

many_users = [hello() for i in range(100)]

asyncio.get_event_loop().run_until_complete(asyncio.gather(*many_users))
