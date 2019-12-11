import json
import logging
import asyncio
import websockets

from explorebaduk.constants import LOGIN, LOGOUT, OK, ERROR
from explorebaduk.database import TokenModel, UserModel
from explorebaduk.schema import LoginSchema
from explorebaduk.models import Player
from explorebaduk.server import eb_server

logger = logging.getLogger("auth")


def login_ok_event():
    return json.dumps({'type': LOGIN, 'result': OK})


def logout_ok_event():
    return json.dumps({'type': LOGOUT, 'result': OK})


def login_error_event(message: str):
    return json.dumps({'type': LOGIN, 'result': ERROR, 'error_message': 'Invalid token'})


async def handle_login(ws, data: dict):
    player: Player = eb_server.users[ws]
    if player.logged_in:
        await ws.send(login_error_event('Already logged in'))

    else:
        # Authenticate user
        signin_data = LoginSchema().load(data)
        signin_token = eb_server.session.query(TokenModel).filter_by(**signin_data).first()

        if not signin_token:
            await ws.send(login_error_event('Invalid token'))

        else:
            user = eb_server.session.query(UserModel).filter_by(user_id=signin_token.user_id).first()
            player.login_as(user)
            await asyncio.gather(ws.send(login_ok_event()), eb_server.notify_users())


async def handle_logout(ws: websockets.WebSocketServerProtocol):
    eb_server.users[ws] = None
    await asyncio.gather(ws.send(logout_ok_event()), eb_server.notify_users())


async def handle_auth(ws, action: str, data: dict):
    if action == LOGIN:
        await handle_login(ws, data)

    elif action == LOGOUT:
        await handle_logout(ws)
