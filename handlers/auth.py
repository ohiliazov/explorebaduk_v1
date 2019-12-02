import asyncio
import json
import logging

from constants import AuthAction
from database import SignInToken, User
from schema import LoginPayload

logger = logging.getLogger("eb_auth")


async def handle_login(session, ws, data):
    from server import GameServer

    signin_data = LoginPayload().load(data)
    signin_token = session.query(SignInToken).filter_by(**signin_data).first()

    if not signin_token:
        logger.info("Authentication failed for: %s", signin_data)
        return await ws.send(json.dumps({"status": "failure", "message": "Authentication failed"}))

    player = session.query(User).filter_by(user_id=signin_token.user_id).first()

    logger.info("User online: %s", player.email)
    await ws.send(json.dumps({"status": "success", "message": f"Logged in as {player.email}"}))

    GameServer.clients[ws] = player
    message = {
        "target": "user_online",
        "data": {
            "email": player.email,
        },
    }
    message = json.dumps(message)
    await asyncio.wait([player.send(message) for player in GameServer.clients])


async def handle_logout(session, ws, data):
    from server import GameServer
    GameServer.clients[ws] = None


async def handle_auth(session, ws, action: AuthAction, data: dict):
    if action == AuthAction.LOGIN:
        handle_func = handle_login
    else:
        raise NotImplementedError

    await handle_func(session, ws, data)
