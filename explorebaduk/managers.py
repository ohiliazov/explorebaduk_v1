from collections import defaultdict
from typing import Dict, List

from fastapi import WebSocket

from explorebaduk.messages import Notifier

from .models import UserModel


class UsersManager:
    user_ids: Dict[int, List[WebSocket]] = defaultdict(list)

    @classmethod
    def clear(cls):
        cls.user_ids.clear()

    @classmethod
    async def add(cls, user: UserModel, websocket: WebSocket):
        if user.user_id not in cls.user_ids:
            cls.user_ids[user.user_id].append(websocket)
            if len(cls.user_ids[user.user_id]) == 1:
                await Notifier.player_online(user)

    @classmethod
    async def remove(cls, user: UserModel, websocket: WebSocket):
        cls.user_ids[user.user_id].remove(websocket)

    @classmethod
    def is_online(cls, user: UserModel) -> bool:
        return bool(cls.user_ids[user.user_id])

    @classmethod
    def get_user_ids(cls, user: UserModel = None) -> List[int]:
        user_ids = [user_id for user_id in cls.user_ids]
        if user:
            user_ids.remove(user.user_id)
        return user_ids
