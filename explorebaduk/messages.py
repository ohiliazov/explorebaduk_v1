from typing import Any, Optional

import simplejson as json

from .models import UserModel


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


class AuthorizeMessage(Message):
    event = "authorize"

    def __init__(self, token: str = None):
        self.data = token


class WhoAmIMessage(Message):
    event = "whoami"

    def __init__(self, user: Optional[UserModel]):
        self.data = user.asdict() if user else None


class PlayerInfoMixin:
    @staticmethod
    def make_players_data(user: UserModel):
        return {
            "status": "online",
            **user.asdict(),
        }


class PlayerOnlineMessage(Message, PlayerInfoMixin):
    event = "players.add"

    def __init__(self, user: UserModel):
        self.data = self.make_players_data(user)


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
    event = "challenges.direct.remove"

    def __init__(self, challenge_id: int):
        self.data = {"challenge_id": challenge_id}


class GameStartedMessage(Message):
    event = "games.start"

    def __init__(self, game: dict):
        self.data = game
