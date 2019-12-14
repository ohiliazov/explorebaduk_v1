import asyncio
import json
import websockets
import random

login_message = {
    'type': 'login',
    'data': {
        'user_id': 1,
        'token': f'token_1'
    }
}
logout_message = {
    'type': 'logout',
    'data': ''
}

challenge_message = {
    'type': 'challenge',
    'action': 'create',
    'data': {
        'type': 'ranked',
        'name': 'My Challenge Name',
        'rule_set': {
            'rules': 'japanese',
            'board_height': 19,
            'to_join': 1,
        },
        'restrictions': {
            'no_undo': False,
            'no_pause': False,
            'no_analyze': False,
            'is_private': False,
        },
        'time_system': {
            'type': 'absolute',
            'main': 3600,
        }
    }
}


async def hello():
    uri = "ws://localhost:8080"
    async with websockets.connect(uri) as websocket:
        while True:
            message = input("> ")

            if message == 'get':
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=0.1)
                    print('<', response)
                except:
                    pass

            elif message == 'login':
                await websocket.send(json.dumps(login_message))
            elif message == 'logout':
                await websocket.send(json.dumps(logout_message))
            elif message == 'challenge':
                await websocket.send(json.dumps(challenge_message))
            else:
                await websocket.send(message)

asyncio.get_event_loop().run_until_complete(hello())
