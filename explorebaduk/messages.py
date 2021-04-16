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


class UserIdMessage(Message):
    def __init__(self, user: UserModel):
        self.data = {"user_id": user.user_id}


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


class PlayerOfflineMessage(UserIdMessage):
    event = "players.remove"


class OpenGameCreatedMessage(Message):
    event = "games.open.add"

    def __init__(self, user: UserModel, game: dict):
        self.data = {"user_id": user.user_id, **game}


class OpenGameRemoveMessage(UserIdMessage):
    event = "games.open.remove"


class CreateOpenGameRequestMessage(Message):
    event = "games.open.request.create"

    def __init__(self, user: UserModel, game_settings: dict):
        self.data = {"user_id": user.user_id, "settings": game_settings}


class RemoveOpenGameRequestMessage(UserIdMessage):
    event = "games.open.request.remove"


class AcceptOpenGameRequestMessage(UserIdMessage):
    event = "games.open.request.accept"


class RejectOpenGameRequestMessage(UserIdMessage):
    event = "games.open.request.reject"


class GameInviteAddMessage(OpenGameCreatedMessage):
    event = "games.direct.add"


class GameInviteRemoveMessage(UserIdMessage):
    event = "games.direct.remove"


class GameInviteAcceptMessage(UserIdMessage):
    event = "games.direct.request.accept"


class GameInviteRejectMessage(UserIdMessage):
    event = "games.direct.request.reject"
