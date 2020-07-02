import asyncio

from explorebaduk.database import DatabaseHandler
from explorebaduk.helpers import send_sync_messages
from explorebaduk.models import User
from explorebaduk.server import USERS


def is_logged_in(ws):
    return USERS.get(ws)


def get_user_by_token(ws, token: str, db_handler: DatabaseHandler):
    signin_token = db_handler.select_token(token)

    if signin_token:
        return User(ws, signin_token.user)


def is_logged_in_from_another_device(auth_user: User):
    return any((user.id == auth_user.id for user in USERS.values() if user))


async def login_user(user: User):
    USERS[user.ws] = user
    await asyncio.gather(
        user.send(f"auth/login: {user}"),
        send_sync_messages(f"sync/players add {user}"),
    )


async def logout_user(ws):
    user = USERS.pop(ws)

    await asyncio.gather(
        ws.send(f"auth/logout: {user}"),
        send_sync_messages(f"sync/players del {user}"),
    )


async def handle_auth_login(ws, data: dict, db_handler: DatabaseHandler):
    """Login player"""
    if is_logged_in(ws):
        return await ws.send("auth/login: already logged in")

    user = get_user_by_token(ws, data["token"], db_handler)

    if not user:
        return await ws.send("auth/login: invalid token")

    if is_logged_in_from_another_device(user):
        return await ws.send("auth/login: online from other device")

    await login_user(user)


async def handle_auth_logout(ws, data, db_handler: DatabaseHandler):
    """Logout player"""
    if not is_logged_in(ws):
        return await ws.send("auth/login: not logged in")

    await logout_user(ws)
