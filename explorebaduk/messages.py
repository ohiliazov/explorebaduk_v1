from typing import Any, Iterable, Optional

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


class RefreshMessage(Message):
    event = "refresh"

    def __init__(self):
        self.data = None


class WhoAmIMessage(Message):
    event = "whoami"

    def __init__(self, user: Optional[UserModel]):
        self.data = user.as_dict() if user else None


class PlayerInfoMixin:
    @staticmethod
    def make_players_data(user: UserModel):
        return {
            "status": "online",
            **user.as_dict(),
        }


class PlayerListMessage(Message, PlayerInfoMixin):
    event = "players.list"

    def __init__(self, users: Iterable[UserModel]):
        users = sorted(users, key=lambda user: (-user.rating, user.username))
        self.data = [self.make_players_data(user) for user in users]


class OpenGamesMessage(Message, PlayerInfoMixin):
    event = "games.open.list"

    def __init__(self, challenges: dict):
        self.data = [
            {"user_id": user_id, **challenge.dict()}
            for user_id, challenge in challenges.items()
        ]


class PlayerOnlineMessage(Message, PlayerInfoMixin):
    event = "players.add"

    def __init__(self, user: UserModel):
        self.data = self.make_players_data(user)


class PlayerOfflineMessage(Message):
    event = "players.remove"

    def __init__(self, user: UserModel = None):
        self.data = {"user_id": user.user_id if user else None}


class OpenGameCreatedMessage(Message):
    event = "games.open.add"

    def __init__(self, user: UserModel, challenge: dict):
        self.data = {
            "user_id": user.user_id,
            **challenge,
        }


class OpenGameCancelledMessage(Message):
    event = "games.open.remove"

    def __init__(self, user: UserModel = None):
        self.data = {"user_id": user.user_id if user else None}


class DirectInvitesMessage(OpenGamesMessage):
    event = "games.direct.list"


class DirectInviteCreatedMessage(OpenGameCreatedMessage):
    event = "games.direct.add"


class DirectInviteCancelledMessage(OpenGameCancelledMessage):
    event = "games.direct.remove"
