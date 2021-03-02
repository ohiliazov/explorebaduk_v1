from typing import List

from explorebaduk.messages import PlayerListMessage
from explorebaduk.models import UserModel


class MessageHelper:
    @staticmethod
    def player_list(users: List[UserModel]) -> dict:
        return PlayerListMessage(users).json()
