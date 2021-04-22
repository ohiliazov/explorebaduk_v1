from explorebaduk.messages import (
    ChallengeAddMessage,
    ChallengeIncomingAddMessage,
    ChallengeIncomingRemoveMessage,
    ChallengeOpenRemoveMessage,
    ChallengeOutgoingAddMessage,
    ChallengeOutgoingRemoveMessage,
    GameStartedMessage,
    Message,
    PlayerOfflineMessage,
    PlayerOnlineMessage,
)
from explorebaduk.models import UserModel

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
    async def challenge_created(cls, challenge: dict):
        await cls.broadcast(ChallengeAddMessage(challenge))

    @classmethod
    async def challenge_cancelled(cls, challenge_id: int):
        await cls.broadcast(ChallengeOpenRemoveMessage(challenge_id))

    @classmethod
    async def direct_challenge_created(cls, challenge: dict):
        await cls.notify(
            challenge["creator_id"],
            ChallengeOutgoingAddMessage(challenge),
        )
        await cls.notify(
            challenge["opponent_id"],
            ChallengeIncomingAddMessage(challenge),
        )

    @classmethod
    async def direct_challenge_cancelled(cls, challenge: dict):
        await cls.notify(
            challenge["creator_id"],
            ChallengeOutgoingRemoveMessage(challenge["challenge_id"]),
        )
        await cls.notify(
            challenge["opponent_id"],
            ChallengeIncomingRemoveMessage(challenge["challenge_id"]),
        )

    @classmethod
    async def challenge_accepted(cls, game: dict):
        await cls.notify(game["creator_id"], GameStartedMessage(game))
        await cls.notify(game["opponent_id"], GameStartedMessage(game))

        await cls.broadcast(GameStartedMessage(game))


def seconds_to_str(seconds: int) -> str:
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    weeks, days = divmod(days, 7)

    time_str = ""
    if weeks:
        time_str += f"{weeks}w"
    if days:
        time_str += f" {days}d"
    if hours:
        time_str += f" {hours}h"
    if minutes:
        time_str += f" {minutes}m"
    if seconds:
        time_str += f" {seconds}s"

    return time_str
