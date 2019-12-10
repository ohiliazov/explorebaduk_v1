import json
import logging

import websockets

from explorebaduk.constants import USER_LOGIN, USER_LOGOUT
from explorebaduk.database import TokenModel, UserModel
from explorebaduk.schema import LoginSchema
from explorebaduk.server import eb_server

logger = logging.getLogger("user_handler")


async def handle_login(ws, data: dict):
    # Check if user is already logged in
    if ws in eb_server.users:
        data = {
            "status": "success",
            "message": f"Logged in as {eb_server.users[ws].full_name}",
        }

        return await eb_server.send_message(ws, "login", data)

    # Authenticate user
    signin_data = LoginSchema().load(data)
    signin_token = eb_server.session.query(TokenModel).filter_by(**signin_data).first()

    if not signin_token:
        data = {
            "status": "failure",
            "message": "Invalid token",
        }
        return await eb_server.send_message(ws, "login", data)

    # Set user online
    user = eb_server.session.query(UserModel).filter_by(user_id=signin_token.user_id).first()
    eb_server.users[ws] = user
    message = {
        "action": "login",
        "status": "success",
        "data": f"Logged in as {user.full_name}"
    }

    await eb_server.send_message(ws, message)
    await eb_server.sync_all_users({"user_online": user.full_name})


async def handle_logout(ws: websockets.WebSocketServerProtocol):
    # Sync if user was online before
    if ws in eb_server.users_online:
        user = eb_server.users_online.pop(ws)
        await eb_server.sync_all_users({"user_offline": user.full_name})

    # Return message anyway
    data = {
        "status": "success",
        "message": "Logged out",
    }
    await eb_server.send_message(ws, "login", data)


async def handle_user(ws, action: str, data: dict):
    if action == USER_LOGIN:
        await handle_login(ws, data)

    elif action == USER_LOGOUT:
        await handle_logout(ws)
