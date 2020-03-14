import asyncio

from explorebaduk.database import TokenModel, UserModel
from explorebaduk.exceptions import MessageHandlerError
from explorebaduk.helpers import get_player_by_id, send_sync_messages
from explorebaduk.models import Player
from explorebaduk.server import PLAYERS, db


async def handle_auth_login(ws, data: dict):
    """Login player"""
    if ws in PLAYERS:
        raise MessageHandlerError("already logged in")

    # Authenticate user
    signin_token = db.query(TokenModel).filter_by(token=data["token"]).first()

    if not signin_token:
        raise MessageHandlerError("invalid token")

    user_id = signin_token.user_id

    if get_player_by_id(user_id):
        raise MessageHandlerError("online from other device")

    user = db.query(UserModel).filter_by(user_id=user_id).first()
    player = Player(ws, user)

    PLAYERS[ws] = player

    await asyncio.gather(ws.send(f"OK [auth login] {player}"), send_sync_messages(f"players add {player}"))


async def handle_auth_logout(ws, data):
    """Logout player"""
    if ws not in PLAYERS:
        raise MessageHandlerError("not logged in")

    player = PLAYERS.pop(ws)

    await asyncio.gather(ws.send(f"OK [auth logout] {player}"), send_sync_messages(f"players del {player}"))
