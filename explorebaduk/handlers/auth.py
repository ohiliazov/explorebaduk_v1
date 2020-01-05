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


logout_ok_event = "OK auth logout"


def login_error_event(error_message: str):
    return json.dumps({'type': LOGIN, 'result': ERROR, 'error_message': error_message})


async def handle_login(ws: websockets.WebSocketServerProtocol, data: dict):
    player: Player = PLAYERS[ws]
    if player.logged_in:
        logger.info(f"{ws.remote_address} already logged in as {player.user.full_name}")
        return await ws.send(f'ERROR auth: already logged in as {player.user.full_name}')

    # Authenticate user
    signin_data = LoginSchema().load(data)
    signin_token = db.query(TokenModel).filter_by(**signin_data).first()

    if not signin_token:
        logger.info(f"{ws.remote_address} invalid token")
        return await ws.send('ERROR auth: invalid token')

    user = db.query(UserModel).filter_by(user_id=signin_token.user_id).first()
    player.login(user)
    logger.info(f"{ws.remote_address} logged in as {player.user.full_name}")
    return await asyncio.gather(ws.send(f"OK auth: logged in as {player.user.full_name}"), notify_players())


async def handle_logout(ws: websockets.WebSocketServerProtocol):
    PLAYERS[ws].logout()
    await asyncio.gather(ws.send("OK auth: logged out"), notify_players())


async def handle_auth(ws: websockets.WebSocketServerProtocol, data: dict):
    action = data.pop('action')

    if action == LOGIN:
        return await handle_login(ws, data)

    if action == LOGOUT:
        return await handle_logout(ws)
