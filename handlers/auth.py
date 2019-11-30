import asyncio
import json

from constants import AuthAction
from database import SignInToken, User
from schema import AuthPayload, LoginPayload


async def handle_login(ws, payload):
    from server import CONNECTED, db

    data = LoginPayload().load(payload)
    signin_token = db.first(SignInToken, **data)

    if not signin_token:
        return await ws.send(json.dumps({"status": "failure", "message": "Authentication failed"}))

    player = db.first(User, user_id=signin_token.user_id)

    await ws.send(json.dumps({"status": "success", "message": f"Logged in as {player.email}"}))

    CONNECTED[ws] = player
    message = {
        "action": "player_online",
        "player": {
            "username": player.email,
        },
    }
    message = json.dumps(message)
    await asyncio.wait([player.send(message) for player in CONNECTED])


AUTH_HANDLERS = {
    AuthAction.LOGIN: handle_login,
}


async def handle_auth(ws, payload: dict):
    payload = AuthPayload().load(payload)
    auth_action = AuthAction(payload['auth_action'])
    handle_func = AUTH_HANDLERS[auth_action]
    await handle_func(ws, payload)
