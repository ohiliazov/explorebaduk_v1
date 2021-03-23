from explorebaduk.messages import (
    AcceptOpenGameRequestMessage,
    CreateOpenGameRequestMessage,
    GameInviteAcceptMessage,
    GameInviteAddMessage,
    GameInviteRejectMessage,
    GameInviteRemoveMessage,
    Message,
    OpenGameCreatedMessage,
    OpenGameRemoveMessage,
    PlayerOfflineMessage,
    PlayerOnlineMessage,
    RejectOpenGameRequestMessage,
    RemoveOpenGameRequestMessage,
)
from explorebaduk.models import UserModel
from explorebaduk.schemas import GameSettings, GameSetup, OpenGame

from .broadcast import broadcast


class Notifier:
    @staticmethod
    async def broadcast(message: Message):
        await broadcast.publish("main", message.json())

    @staticmethod
    async def notify(user_id, message: Message):
        await broadcast.publish(f"user__{user_id}", message.json())

    @classmethod
    async def player_online(cls, user: UserModel):
        await cls.broadcast(PlayerOnlineMessage(user))

    @classmethod
    async def player_offline(cls, user: UserModel):
        await cls.broadcast(PlayerOfflineMessage(user))

    @classmethod
    async def add_open_game(cls, user: UserModel, game: OpenGame):
        await cls.broadcast(OpenGameCreatedMessage(user, game.dict()))

    @classmethod
    async def remove_open_game(cls, user: UserModel):
        await cls.broadcast(OpenGameRemoveMessage(user))

    @classmethod
    async def create_open_game_request(cls, user_id: int, user: UserModel, settings: GameSettings):
        await cls.notify(user_id, CreateOpenGameRequestMessage(user, settings.dict()))

    @classmethod
    async def remove_open_game_request(cls, user_id: int, user: UserModel):
        await cls.notify(user_id, RemoveOpenGameRequestMessage(user))

    @classmethod
    async def accept_open_game_request(cls, user_id: int, user: UserModel):
        await cls.notify(user_id, AcceptOpenGameRequestMessage(user))

    @classmethod
    async def reject_open_game_request(cls, user_id: int, user: UserModel):
        await cls.notify(user_id, RejectOpenGameRequestMessage(user))

    @classmethod
    async def create_game_invite(cls, user_id: int, user: UserModel, game: GameSetup):
        await cls.notify(user_id, GameInviteAddMessage(user, game.dict()))

    @classmethod
    async def remove_direct_invite(cls, user_id: int, user: UserModel):
        await cls.notify(user_id, GameInviteRemoveMessage(user))

    @classmethod
    async def accept_direct_invite(cls, user_id: int, user: UserModel):
        await cls.notify(user_id, GameInviteAcceptMessage(user))

    @classmethod
    async def reject_direct_invite(cls, user_id: int, user: UserModel):
        await cls.notify(user_id, GameInviteRejectMessage(user))
