import asyncio
import json
import websockets


def login_message(user_id: int = 1):
    return {
        'type': 'login',
        'data': {
            'user_id': user_id,
            'token': f'token_{user_id}'
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

join_message = {
    'type': 'challenge',
    'action': 'join',
    'data': {
        'creator_id': 1,
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

challenge_cancel_message = {
    'type': 'challenge',
    'action': 'cancel',
}


async def hello():
    uri = "ws://localhost:8080"
    async with websockets.connect(uri) as websocket:
        while True:
            try:
                while True:
                    response = await asyncio.wait_for(websocket.recv(), timeout=0.5)
                    print('<', response)
            except asyncio.TimeoutError:
                pass

            message = input("> ")

            if message.startswith('login'):
                user_id = message.split(' ')[-1]
                user_id = int(user_id) if user_id.isdigit() else 1
                await websocket.send(json.dumps(login_message(user_id)))
            elif message == 'logout':
                await websocket.send(json.dumps(logout_message))
            elif message == 'challenge':
                await websocket.send(json.dumps(challenge_message))
            elif message == 'join':
                await websocket.send(json.dumps(join_message))
            elif message == 'cancel':
                await websocket.send(json.dumps(challenge_message))
            else:
                await websocket.send(message)

asyncio.get_event_loop().run_until_complete(hello())
