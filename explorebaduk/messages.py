import logging
from typing import Any, Optional

import simplejson as json

from explorebaduk.broadcast import broadcast
from explorebaduk.models import ChallengeModel, UserModel

logger = logging.getLogger("explorebaduk")
logger.setLevel(logging.INFO)


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


class ChallengeOpenMessage(Message):
    event = "challenges.open.add"

    def __init__(self, challenge: ChallengeModel):
        self.data = challenge.asdict()


class ChallengeAcceptedMessage(Message):
    event = "challenges.open.accept"

    def __init__(self, challenge: ChallengeModel):
        self.data = {
            "challenge_id": challenge.challenge_id,
            "opponent_id": challenge.opponent_id,
            "game_id": challenge.game_id,
        }


class ChallengeRemovedMessage(Message):
    event = "challenges.open.remove"

    def __init__(self, challenge: ChallengeModel):
        self.data = {"challenge_id": challenge.challenge_id}


class DirectChallengeMessage(Message):
    event = "challenges.direct.add"

    def __init__(self, challenge: ChallengeModel):
        self.data = challenge.asdict()


class DirectChallengeRemovedMessage(Message):
    event = "challenges.direct.remove"

    def __init__(self, challenge: ChallengeModel):
        self.data = {"challenge_id": challenge.challenge_id}


class DirectChallengeAcceptedMessage(Message):
    event = "challenges.direct.accept"

    def __init__(self, challenge: ChallengeModel):
        self.data = {
            "challenge_id": challenge.challenge_id,
            "opponent_id": challenge.opponent_id,
            "game_id": challenge.game_id,
        }


class Notifier:
    @staticmethod
    async def broadcast(message: Message):
        logger.info(f">>> [{message.event}] {message.data}")
        await broadcast.publish("main", message.json())

    @staticmethod
    async def notify(user_id, message: Message):
        logger.info(f"> <{user_id}> [{message.event}] {message.data}")
        await broadcast.publish(f"main.user__{user_id}", message.json())

    @classmethod
    async def player_online(cls, user: UserModel):
        await cls.broadcast(PlayerOnlineMessage(user))

    @classmethod
    async def player_offline(cls, user: UserModel):
        await cls.broadcast(PlayerOfflineMessage(user))

    @classmethod
    async def challenge_created(cls, challenge: ChallengeModel):
        await cls.broadcast(ChallengeOpenMessage(challenge))

    @classmethod
    async def challenge_accepted(cls, challenge: ChallengeModel):
        await cls.broadcast(ChallengeAcceptedMessage(challenge))

    @classmethod
    async def challenge_cancelled(cls, challenge: ChallengeModel):
        await cls.broadcast(ChallengeRemovedMessage(challenge))

    @classmethod
    async def direct_challenge_created(cls, challenge: ChallengeModel):
        await cls.notify(challenge.opponent_id, DirectChallengeMessage(challenge))

    @classmethod
    async def direct_challenge_accepted(cls, challenge: ChallengeModel):
        await cls.notify(challenge.creator_id, ChallengeAcceptedMessage(challenge))

    @classmethod
    async def direct_challenge_cancelled(cls, challenge: ChallengeModel):
        await cls.notify(challenge.opponent_id, ChallengeRemovedMessage(challenge))

    @classmethod
    async def direct_challenge_rejected(cls, challenge: ChallengeModel):
        await cls.notify(challenge.creator_id, ChallengeRemovedMessage(challenge))
