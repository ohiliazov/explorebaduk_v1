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
        message = {
            "action": "login",
            "status": "success",
            "data": f"Logged in as {eb_server.users[ws].full_name}",
        }

        return ws.send(json.dumps(message))

    # Authenticate user
    signin_data = LoginSchema().load(data)
    signin_token = eb_server.session.query(TokenModel).filter_by(**signin_data).first()

    if not signin_token:
        message = {
            "action": "login",
            "status": "failure",
            "data": f"Authorization failed",
        }
        return eb_server.send(ws, message)

    # Set user online
    user = eb_server.session.query(UserModel).filter_by(user_id=signin_token.user_id).first()
    eb_server.users[ws] = user
    message = {
        "action": "login",
        "status": "success",
        "data": f"Logged in as {user.full_name}"
    }
    eb_server.sync_all_users(ws, message)

    # Sync all
    sync_message = {
        "action": "sync",
        "data": {"user_online": user.full_name},
    }
    eb_server.sync_all_users(None, sync_message)


async def handle_logout(ws: websockets.WebSocketServerProtocol):
    # Sync if user was online before
    if ws in eb_server.users_online:
        user = eb_server.users_online.pop(ws)
        sync_message = {
            "action": "sync",
            "data": {"user_offline": user.full_name},
        }
        eb_server.sync_all_users(None, sync_message)

    # Return message anyway
    message = {
        "action": "login",
        "status": "success",
        "data": f"Logged out",
    }
    eb_server.sync_all_users(ws, message)


async def handle_user(ws, action: str, data: dict):
    if action == USER_LOGIN:
        await handle_login(ws, data)

    elif action == USER_LOGOUT:
        await handle_logout(ws)
