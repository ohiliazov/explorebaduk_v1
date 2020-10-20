import asyncio

from explorebaduk.database import UserModel
from explorebaduk.mixins import SubscriberMixin


class Player(SubscriberMixin):
    def __init__(self, user: UserModel = None):
        self.ws_list = set()

        self._user = user

        self.lock = asyncio.Lock()

    @property
    def user_id(self):
        return self._user.user_id

    @property
    def authorized(self):
        return self._user is not None

    def as_dict(self):
        if self._user:
            return self._user.as_dict()
