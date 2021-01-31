from typing import Optional

import simplejson as json

from .models import UserModel


class MessageBase:
    event: str
    data: dict

    def __str__(self) -> str:
        return json.dumps({"event": self.event, "data": self.data})

    def json(self) -> dict:
        return json.loads(json.dumps({"event": self.event, "data": self.data}))


class Message(MessageBase):
    def __init__(self, data: dict):
        self.event = data.get("event")
        self.data = data.get("data")

    @classmethod
    def from_string(cls, message: str):
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            data = {}
        return cls(data)


class ErrorMessage(MessageBase):
    event = "error"

    def __init__(self, message: str):
        self.data = {"message": message}


class AuthorizeMessage(MessageBase):
    event = "authorize"

    def __init__(self, token: str = None):
        self.data = {"token": token} if token else None


class WhoAmIMessage(MessageBase):
    event = "whoami"

    def __init__(self, user: Optional[UserModel]):
        self.data = user.as_dict() if user else None


class PlayersAddMessage(MessageBase):
    event = "players.add"

    def __init__(self, user: UserModel, is_friend: bool):
        self.data = {
            "status": "online",  # TODO: remove maybe
            "friend": is_friend,
            **user.as_dict(),
        }


class PlayersRemoveMessage(MessageBase):
    event = "players.remove"

    def __init__(self, user: UserModel = None):
        self.data = {"user_id": user.user_id if user else None}


class ChallengesAddMessage(MessageBase):
    event = "challenges.add"

    def __init__(self, challenge_id: int, challenge: dict):
        self.data = {
            "user_id": challenge_id,
            **challenge,
        }


class ChallengesRemoveMessage(MessageBase):
    event = "challenges.remove"

    def __init__(self, user_id: int):
        self.data = {"user_id": user_id}
