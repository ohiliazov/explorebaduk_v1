import asyncio
from collections import defaultdict
from typing import Dict, List

from fastapi import WebSocket

from .helpers import Notifier
from .models import UserModel
from .schemas import GameSettings, GameSetup, OpenGame

OFFLINE_TIMEOUT = 5


class UsersOnline:
    user_ids: Dict[int, List[WebSocket]] = defaultdict(list)

    @classmethod
    def clear(cls):
        cls.user_ids.clear()

    @classmethod
    async def add(cls, user: UserModel, websocket: WebSocket):
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


class GameRequests:
    open_games: Dict[int, OpenGame] = {}
    open_games_requests: Dict[int, Dict[int, GameSettings]] = defaultdict(dict)
    direct_invites: Dict[int, Dict[int, GameSetup]] = defaultdict(dict)

    @classmethod
    def clear(cls):
        cls.direct_invites.clear()
        cls.open_games_requests.clear()
        cls.open_games.clear()

    @classmethod
    def list_open_games(cls) -> List[OpenGame]:
        return [open_game for open_game in cls.open_games.values()]

    @classmethod
    def get_open_game(cls, user_id: int):
        return cls.open_games.get(user_id)

    @classmethod
    async def set_open_game(cls, user: UserModel, open_game: OpenGame):
        cls.open_games[user.user_id] = open_game
        await Notifier.add_open_game(user, open_game)

    @classmethod
    async def remove_open_game(cls, user: UserModel):
        cls.open_games_requests.pop(user.user_id, None)
        if cls.open_games.pop(user.user_id, None):
            await Notifier.remove_open_game(user)

    @classmethod
    async def create_open_game_request(cls, user_id, opponent: UserModel, settings: GameSettings):
        cls.open_games_requests[user_id][opponent.user_id] = settings
        await Notifier.create_open_game_request(user_id, opponent, settings)

    @classmethod
    async def remove_open_game_request(cls, user_id, opponent: UserModel):
        if cls.open_games_requests[user_id].pop(opponent.user_id, None):
            await Notifier.remove_open_game_request(user_id, opponent)

    @classmethod
    async def accept_open_game_request(cls, user: UserModel, opponent_id: int):
        await Notifier.accept_open_game_request(opponent_id, user)
        await cls.remove_open_game(user)

    @classmethod
    async def reject_open_game_request(cls, user: UserModel, opponent_id: int):
        cls.open_games_requests[user.user_id].pop(opponent_id)
        await Notifier.reject_open_game_request(opponent_id, user)

    @classmethod
    def get_open_game_request(cls, user_id: int, opponent_id: int):
        return cls.open_games_requests[user_id][opponent_id]

    @classmethod
    def get_direct_invites(cls, user_id) -> Dict[int, GameSetup]:
        return cls.direct_invites[user_id]

    @classmethod
    async def create_direct_invite(
        cls,
        opponent_id: int,
        user: UserModel,
        game_setup: GameSetup,
    ):
        cls.direct_invites[user.user_id][opponent_id] = game_setup
        await Notifier.create_game_invite(opponent_id, user, game_setup)

    @classmethod
    async def remove_direct_invite(cls, opponent_id: int, user: UserModel):
        await Notifier.remove_direct_invite(opponent_id, user)
        cls.direct_invites[user.user_id].pop(opponent_id)

    @classmethod
    async def accept_direct_invite(cls, opponent_id, user: UserModel):
        await Notifier.accept_direct_invite(opponent_id, user)
        cls.direct_invites[opponent_id].pop(user.user_id)

    @classmethod
    async def reject_direct_invite(cls, opponent_id, user: UserModel):
        await Notifier.reject_direct_invite(opponent_id, user)
        cls.direct_invites[opponent_id].pop(user.user_id)

    @classmethod
    async def clear_direct_invites(cls, user: UserModel):
        direct_invites = cls.direct_invites[user.user_id]

        if direct_invites:
            await asyncio.wait([cls.remove_direct_invite(opponent_id, user) for opponent_id in direct_invites])
