import json

import websockets
from marshmallow import ValidationError

from constants import Target
from handlers.auth import handle_auth
from schema import WebSocketMessage


async def handle_message(session, ws: websockets.WebSocketServerProtocol, data: dict):
    try:
        target, action = WebSocketMessage().load(data)

        data.pop('target')
        data.pop('action')

        if target == Target.AUTH:
            handle_func = handle_auth
        else:
            raise NotImplementedError

        return await handle_func(session, ws, action, data)
    except ValidationError as err:
        message = {"status": "failure", "errors": err.messages}
        return await ws.send(json.dumps(message))
