import logging
import asyncio

from explorebaduk.constants import LoginAction
from explorebaduk.database import TokenModel, UserModel
from explorebaduk.models import User
from explorebaduk.server import USERS, notify_users, db


logger = logging.getLogger("auth")


# login messages
LOGGED_IN = "OK auth login: logged in"
ALREADY_LOGGED_IN = "ERROR auth login: already logged in"
ALREADY_ONLINE = "ERROR auth login: already online from on another device"
USER_NOT_FOUND = "ERROR auth login: user not found"
INVALID_TOKEN = "ERROR auth login: invalid token"

# logout messages
LOGGED_OUT = "OK auth logout: logged out"
NOT_LOGGED_IN = "ERROR auth logout: not logged in"


async def handle_login(ws, data: dict):
    """Login player"""
    logger.info("handle_login")

    if ws in USERS:
        return await ws.send(ALREADY_LOGGED_IN)

    # Authenticate user
    signin_token = db.query(TokenModel).filter_by(token=data["token"]).first()

    if not signin_token:
        return await ws.send(INVALID_TOKEN)

    user_id = signin_token.user_id
    user = db.query(UserModel).filter_by(user_id=user_id).first()

    if any([user.id == user_id for user in USERS.values() if user]):
        return await ws.send(ALREADY_ONLINE)

    USERS[ws] = User(ws, user)

    return await asyncio.gather(ws.send(LOGGED_IN), notify_users())


async def handle_logout(ws):
    """Logout player"""
    logger.info("handle_logout")

    if ws not in USERS:
        return await ws.send(NOT_LOGGED_IN)

    del USERS[ws]

    return await asyncio.gather(ws.send(LOGGED_OUT), notify_users())


async def handle_auth(ws, data: dict):
    logger.info("handle_auth")

    action = LoginAction(data.pop("action"))

    if action is LoginAction.LOGIN:
        await handle_login(ws, data)

    elif action is LoginAction.LOGOUT:
        await handle_logout(ws)

    else:
        await ws.send(f"ERROR auth {action.value}: not implemented")
