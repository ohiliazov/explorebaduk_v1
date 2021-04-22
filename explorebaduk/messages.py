from typing import Any, Optional

import simplejson as json

from explorebaduk.broadcast import broadcast
from explorebaduk.models import UserModel


class Message:
    event: str
    data: Any

    def __str__(self) -> str:
        return json.dumps({"event": self.event, "data": self.data})

    def json(self) -> dict:
        return json.loads(json.dumps({"event": self.event, "data": self.data}))

    def __eq__(self, other: "Message"):
        return self.event == other.event and self.data == other.data


class ReceivedMessage(Message):
    def __init__(self, data: Any):
        self.event = data.get("event")
        self.data = data.get("data")

    @classmethod
    def from_string(cls, message: str):
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            data = {}
        return cls(data)


class WhoAmIMessage(Message):
    event = "whoami"

    def __init__(self, user: Optional[UserModel]):
        self.data = user.asdict() if user else None


class PlayerOnlineMessage(Message):
    event = "players.add"

    def __init__(self, user: UserModel):
        self.data = {
            "status": "online",
            **user.asdict(),
        }


class PlayerOfflineMessage(Message):
    event = "players.remove"

    def __init__(self, user: UserModel):
        self.data = {"user_id": user.user_id}


class ChallengeAddMessage(Message):
    event = "challenges.open.add"

    def __init__(self, challenge: dict):
        self.data = challenge


class ChallengeIncomingAddMessage(Message):
    event = "challenges.incoming.add"

    def __init__(self, challenge: dict):
        self.data = challenge


class ChallengeOutgoingAddMessage(Message):
    event = "challenges.outgoing.add"

    def __init__(self, challenge: dict):
        self.data = challenge


class ChallengeOpenRemoveMessage(Message):
    event = "challenges.open.remove"

    def __init__(self, challenge_id: int):
        self.data = {"challenge_id": challenge_id}


class ChallengeIncomingRemoveMessage(Message):
    event = "challenges.incoming.remove"

    def __init__(self, challenge_id: int):
        self.data = {"challenge_id": challenge_id}


class ChallengeOutgoingRemoveMessage(Message):
    event = "challenges.outgoing.remove"

    def __init__(self, challenge_id: int):
        self.data = {"challenge_id": challenge_id}


class ChallengeAcceptedMessage(Message):
    event = "challenges.accept"

    def __init__(self, challenge_id: int, opponent_id: int):
        self.data = {"challenge_id": challenge_id, "opponent_id": opponent_id}


class GameStartedMessage(Message):
    event = "games.add"

    def __init__(self, game_id: int):
        self.data = {"game_id": game_id}


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
    async def game_started(cls, game_id: int, creator_id: int, opponent_id: int):
        await cls.notify(creator_id, GameStartedMessage(game_id))
        await cls.notify(opponent_id, GameStartedMessage(game_id))
