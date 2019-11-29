import asyncio
import json
import websockets


async def hello():
    uri = "ws://localhost:8080"
    logged_in = False
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({'action': 'login', 'username': 'Alex'}))

        async for message in websocket:
            data = json.loads(message)
            if not logged_in:
                expected = {'status': 'success',
                            'message': 'Logged in as Alex'}
                if data == expected:
                    logged_in = True

            print(logged_in, data)

asyncio.get_event_loop().run_until_complete(hello())
