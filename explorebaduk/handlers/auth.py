import json
import logging
import asyncio
import websockets

from explorebaduk.constants import LOGIN, LOGOUT, OK, ERROR
from explorebaduk.database import TokenModel, UserModel
from explorebaduk.schema import LoginSchema
from explorebaduk.models import Player
from explorebaduk.server import PLAYERS, notify_players, db

logger = logging.getLogger("auth")


login_ok_event = json.dumps({'type': LOGIN, 'result': OK})
logout_ok_event = json.dumps({'type': LOGOUT, 'result': OK})


def login_error_event(error_message: str):
    return json.dumps({'type': LOGIN, 'result': ERROR, 'error_message': error_message})


async def handle_login(ws: websockets.WebSocketServerProtocol, data: dict):
    player: Player = PLAYERS[ws]
    if player.logged_in:
        logger.info(f"{ws.remote_address} already logged in as {player.user.full_name}")
        return await ws.send(login_error_event('Already logged in'))

    # Authenticate user
    signin_data = LoginSchema().load(data)
    signin_token = db.query(TokenModel).filter_by(**signin_data).first()

    if not signin_token:
        logger.info(f"{ws.remote_address} invalid token")
        return await ws.send(login_error_event('Invalid token'))

    user = db.query(UserModel).filter_by(user_id=signin_token.user_id).first()
    player.login_as(user)
    logger.info(f"{ws.remote_address} logged in as {player.user.full_name}")
    return await asyncio.gather(ws.send(login_ok_event), notify_players())


async def handle_logout(ws: websockets.WebSocketServerProtocol):
    PLAYERS[ws].logout()
    await asyncio.gather(ws.send(logout_ok_event), notify_players())
