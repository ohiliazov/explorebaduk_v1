from collections import defaultdict
from typing import List

from fastapi import WebSocket

from explorebaduk.models import UserModel
from explorebaduk.logger import logger


ONLINE_PLAYERS = defaultdict(list)


def clear_server_state():
    ONLINE_PLAYERS.clear()


def is_player_online(user: UserModel) -> bool:
    return bool(user and ONLINE_PLAYERS[user.user_id])


def get_player_ids() -> List[int]:
    return list(filter(bool, ONLINE_PLAYERS))


def add_player_ws(user: UserModel, websocket: WebSocket):
    ONLINE_PLAYERS[user.user_id].append(websocket)


def remove_player_ws(user: UserModel, websocket: WebSocket):
    try:
        ONLINE_PLAYERS[user.user_id].remove(websocket)
    except ValueError:
        logger.warning("Websocket is not related to player.")
