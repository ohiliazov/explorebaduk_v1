import json

from typing import Optional

from explorebaduk.database import UserModel


class Player:
    def __init__(self, ws):
        self.ws = ws
        self.user: Optional[UserModel] = None

    async def send(self, data: str):
        return self.ws.send(json.dumps(data))

    @property
    def logged_in(self):
        return self.user is not None

    @property
    def id(self):
        return self.user.user_id

    @property
    def full_name(self):
        return self.user.full_name

    def login_as(self, user: UserModel):
        self.user = user

    def logout(self):
        self.user = None
