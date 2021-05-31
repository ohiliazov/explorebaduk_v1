from collections import defaultdict
from typing import Dict, List

from fastapi import WebSocket

from explorebaduk.models import UserModel


class UsersOnline:
    user_ids: Dict[int, List[WebSocket]] = defaultdict(list)

    @classmethod
    def clear(cls):
        cls.user_ids.clear()

    @classmethod
    def add(cls, user: UserModel, websocket: WebSocket):
        cls.user_ids[user.user_id].append(websocket)

    @classmethod
    def remove(cls, user: UserModel, websocket: WebSocket):
        cls.user_ids[user.user_id].remove(websocket)

    @classmethod
    def is_online(cls, user: UserModel) -> bool:
        return bool(cls.user_ids[user.user_id])

    @classmethod
    def is_only_connection(cls, user: UserModel) -> bool:
        return len(cls.user_ids[user.user_id]) == 1

    @classmethod
    def get_user_ids(cls, user: UserModel = None) -> List[int]:
        user_ids = [user_id for user_id in cls.user_ids]
        if user:
            user_ids.remove(user.user_id)
        return user_ids
