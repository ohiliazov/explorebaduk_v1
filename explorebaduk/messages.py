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


class ErrorMessage(Message):
    event = "error"

    def __init__(self, message: str):
        self.data = {"message": message}


class AuthorizeMessage(Message):
    event = "authorize"

    def __init__(self, token: str = None):
        self.data = {"token": token} if token else None


class WhoAmIMessage(Message):
    event = "whoami"

    def __init__(self, user: Optional[UserModel]):
        self.data = user.as_dict() if user else None


class PlayerInfoMixin:
    @staticmethod
    def make_players_data(user: UserModel, current_user: Optional[UserModel] = None):
        return {
            "status": "online",
            "friend": current_user.is_friend(user.user_id) if current_user else False,
            **user.as_dict(),
        }


class PlayerListMessage(Message, PlayerInfoMixin):
    event = "players.list"

    def __init__(
        self,
        users: Iterable[UserModel],
        current_user: Optional[UserModel] = None,
    ):
        self.data = [self.make_players_data(user, current_user) for user in users]


class PlayersAddMessage(Message, PlayerInfoMixin):
    event = "players.add"

    def __init__(self, user: UserModel, current_user: Optional[UserModel] = None):
        self.data = self.make_players_data(user, current_user)


class PlayersRemoveMessage(Message):
    event = "players.remove"

    def __init__(self, user: UserModel = None):
        self.data = {"user_id": user.user_id if user else None}
