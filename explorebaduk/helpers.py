from explorebaduk.messages import (
    GameInviteAcceptMessage,
    GameInviteAddMessage,
    GameInviteRejectMessage,
    GameInviteRemoveMessage,
    Message,
    OpenGameAcceptMessage,
    OpenGameCreatedMessage,
    OpenGameRejectMessage,
    OpenGameRemoveMessage,
    OpenGameRequestMessage,
    PlayerOfflineMessage,
    PlayerOnlineMessage,
)
from explorebaduk.models import UserModel
from explorebaduk.schemas import GameInviteIn, GameSettingsIn, OpenGame

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
    async def open_game_created(cls, user: UserModel, game: OpenGame):
        await cls.broadcast(OpenGameCreatedMessage(user, game.dict()))

    @classmethod
    async def open_game_cancelled(cls, user: UserModel):
        await cls.broadcast(OpenGameRemoveMessage(user))

    @classmethod
    async def open_game_requested(
        cls, user_id: int, user: UserModel, settings: GameSettingsIn
    ):
        await cls.notify(user_id, OpenGameRequestMessage(user, settings.dict()))

    @classmethod
    async def open_game_accepted(cls, user_id: int, user: UserModel):
        await cls.notify(user_id, OpenGameAcceptMessage(user))

    @classmethod
    async def open_game_rejected(cls, user_id: int, user: UserModel):
        await cls.notify(user_id, OpenGameRejectMessage(user))

    @classmethod
    async def game_invite_created(
        cls, user_id: int, user: UserModel, game: GameInviteIn
    ):
        await cls.notify(user_id, GameInviteAddMessage(user, game.dict()))

    @classmethod
    async def game_invite_cancelled(cls, user_id: int, user: UserModel):
        await cls.notify(user_id, GameInviteRemoveMessage(user))

    @classmethod
    async def game_invite_accepted(cls, user_id: int, user: UserModel):
        await cls.notify(user_id, GameInviteAcceptMessage(user))

    @classmethod
    async def game_invite_rejected(cls, user_id: int, user: UserModel):
        await cls.notify(user_id, GameInviteRejectMessage(user))
