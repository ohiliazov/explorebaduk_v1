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


def login_error_event(error_message: str):
    return json.dumps({'type': LOGIN, 'result': ERROR, 'error_message': error_message})


async def handle_login(ws: websockets.WebSocketServerProtocol, data: dict):
    player: Player = eb_server.users[ws]
    if player.logged_in:
        logger.info(f"{ws.remote_address} already logged in as {player.user.full_name}")
        return await ws.send(login_error_event('Already logged in'))

    # Authenticate user
    signin_data = LoginSchema().load(data)
    signin_token = eb_server.session.query(TokenModel).filter_by(**signin_data).first()

    if not signin_token:
        logger.info(f"{ws.remote_address} invalid token")
        return await ws.send(login_error_event('Invalid token'))

    user = eb_server.session.query(UserModel).filter_by(user_id=signin_token.user_id).first()
    player.login_as(user)
    logger.info(f"{ws.remote_address} logged in as {player.user.full_name}")
    return await asyncio.gather(ws.send(login_ok_event()), eb_server.notify_users())


async def handle_logout(ws: websockets.WebSocketServerProtocol):
    eb_server.users[ws].logout()
    await asyncio.gather(ws.send(logout_ok_event()), eb_server.notify_users())


async def handle_auth(ws, action: str, data: dict):
    if action == LOGIN:
        await handle_login(ws, data)

    elif action == LOGOUT:
        await handle_logout(ws)
