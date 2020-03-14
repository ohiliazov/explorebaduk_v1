import logging
import asyncio

from explorebaduk.database import TokenModel, UserModel
from explorebaduk.models import Player
from explorebaduk.server import PLAYERS, db
from explorebaduk.helpers import send_messages, send_sync_messages

logger = logging.getLogger("auth")


def player_joined(player: Player):
    return f"sync player joined {str(player)}"


def player_left(player: Player):
    return f"sync player left {str(player)}"


async def handle_auth_login(ws, data: dict):
    """Login player"""

    if ws in PLAYERS:
        return await ws.send("auth login ERROR already logged in")

    # Authenticate user
    signin_token = db.query(TokenModel).filter_by(token=data["token"]).first()

    if not signin_token:
        return await ws.send("auth login ERROR invalid token")

    user_id = signin_token.user_id
    user = db.query(UserModel).filter_by(user_id=user_id).first()

    if any([user.id == user_id for user in PLAYERS.values() if user]):
        return await ws.send("auth login ERROR online from other device")

    player = Player(ws, user)
    message = f"auth login OK {str(player)}"
    sync_message = player_joined(player)

    PLAYERS[ws] = player

    return await asyncio.gather(send_messages(ws, message), send_sync_messages(sync_message))


async def handle_auth_logout(ws, data):
    """Logout player"""

    if ws not in PLAYERS:
        return await ws.send("auth logout OK")

    player = PLAYERS[ws]



    message = player_left(player)

    del PLAYERS[ws]

    return await asyncio.gather(ws.send("auth logout OK"), send_sync_messages(message))
