import json
import websockets
from marshmallow import ValidationError

from .auth import handle_auth

from constants import Target
from schema import Payload

HANDLERS = {
    Target.AUTH: handle_auth
}


async def handle_message(websocket: websockets.WebSocketServerProtocol, message: str):
    try:
        payload = Payload().loads(message)
        target = Target(payload['target'])
        handle_func = HANDLERS[target]
        return await handle_func(websocket, payload)
    except ValidationError as err:
        message = {"status": "failure",
                   "errors": err.messages}
        return await websocket.send(json.dumps(message))
