import logging
import asyncio

from explorebaduk.constants import LoginAction
from explorebaduk.database import TokenModel, UserModel
from explorebaduk.models import Player
from explorebaduk.schema import LoginSchema
from explorebaduk.server import PLAYERS, notify_players, db

logger = logging.getLogger("auth")


# login messages
LOGGED_IN = "OK auth login: logged in"
ALREADY_LOGGED_IN = "ERROR auth login: already logged in"
USER_NOT_FOUND = "ERROR auth login: user not found"
INVALID_TOKEN = "ERROR auth login: invalid token"

# logout messages
LOGGED_OUT = "OK auth logout: logged out"
NOT_LOGGED_IN = "ERROR auth logout: not logged in"


async def handle_login(ws, data: dict):
    """Login player"""
    logger.info("handle_login")

    player = PLAYERS[ws]

    if player:
        return await ws.send(ALREADY_LOGGED_IN)

    signin_data = LoginSchema().load(data)

    # Authenticate user
    user_id = signin_data["user_id"]
    user = db.query(UserModel).filter_by(user_id=user_id).first()

    if not user:
        return await ws.send(USER_NOT_FOUND)

    signin_token = db.query(TokenModel).filter_by(**signin_data).first()

    if not signin_token:
        return await ws.send(INVALID_TOKEN)

    PLAYERS[ws] = Player(ws, user)

    return await asyncio.gather(ws.send(LOGGED_IN), notify_players())


async def handle_logout(ws):
    """Logout player"""
    logger.info("handle_logout")

    player = PLAYERS[ws]

    if not player:
        return await ws.send(NOT_LOGGED_IN)

    PLAYERS[ws] = None

    return await asyncio.gather(ws.send(LOGGED_OUT), notify_players())


async def handle_auth(ws, data: dict):
    logger.info("handle_auth")

    action = LoginAction(data.pop("action"))

    if action is LoginAction.LOGIN:
        await handle_login(ws, data)

    elif action is LoginAction.LOGOUT:
        await handle_logout(ws)

    else:
        await ws.send(f"ERROR auth {action.value}: not implemented")
