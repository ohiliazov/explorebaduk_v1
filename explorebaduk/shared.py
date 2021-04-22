import asyncio
from collections import defaultdict
from typing import Dict, List

from fastapi import WebSocket

from .crud import DatabaseHandler
from .helpers import Notifier
from .models import ChallengeModel, UserModel

OFFLINE_TIMEOUT = 5


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
        await asyncio.sleep(OFFLINE_TIMEOUT)

        if not cls.user_ids[user.user_id]:
            await Notifier.player_offline(user)

    @classmethod
    def is_online(cls, user: UserModel) -> bool:
        return bool(cls.user_ids[user.user_id])

    @classmethod
    def get_user_ids(cls, user: UserModel = None) -> List[int]:
        user_ids = [user_id for user_id in cls.user_ids]
        if user:
            user_ids.remove(user.user_id)
        return user_ids


class ChallengesManager:
    @classmethod
    def get_open_challenges(cls):
        with DatabaseHandler() as db:
            return [challenge.asdict() for challenge in db.list_challenges()]

    @classmethod
    def get_challenges_in(cls, user_id: int) -> List[ChallengeModel]:
        with DatabaseHandler() as db:
            return db.list_incoming_challenges(user_id)

    @classmethod
    def get_challenges_out(cls, user_id: int) -> List[ChallengeModel]:
        with DatabaseHandler() as db:
            return db.list_outgoing_challenges(user_id)
