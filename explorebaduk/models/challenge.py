import asyncio

from typing import Dict

from explorebaduk.models.user import User
from explorebaduk.constants import RequestStatus, GameType, Ruleset
from explorebaduk.exceptions import JoinRequestError


class JoinRequest:
    def __init__(self, data: dict, status: RequestStatus):
        self.data = data
        self.status = status

    def join(self):
        self.status = RequestStatus.JOINED

    def accept(self):
        self.status = RequestStatus.ACCEPTED


class GameInfo:
    def __init__(
        self,
        name: str,
        game_type: GameType,
        rules: Ruleset,
        width: int,
        height: int,
        min_rating: int = 0,
        max_rating: int = 3000,
        **kwargs,
    ):
        self.name = name
        self.game_type = game_type
        self.rules = rules
        self.width = width
        self.height = height
        self.min_rating = min_rating
        self.max_rating = max_rating


class Challenge:
    def __init__(self, challenge_id: int, creator: User, data: dict):

        self.id = challenge_id
        self.creator = creator
        self.blacklist = set()

        self.game_info = GameInfo(**data)
        self.joined: Dict[User, JoinRequest] = {self.creator: JoinRequest(data, RequestStatus.ACCEPTED)}

        # TODO: remove
        self.name = data.pop("name")
        self.game_type = data.pop("game_type")
        self.rules = data.pop("rules")
        self.data = data

    @property
    def board_size(self):
        return f"{self.data['width']}:{self.data['height']}"

    def __str__(self):
        # TODO: update
        return (
            f"{self.id} {self.name} "
            f"GT{self.game_type.value}RL{self.rules.value}PL{self.players_num} {self.board_size} "
            f"F{int(self.data['is_open'])}{int(self.data['undo'])}{int(self.data['pause'])} "
            f"T{self.data['time_system'].value}M{self.data['main_time']}"
            f"O{self.data['overtime']}P{self.data['periods']}S{self.data['stones']}"
            f"B{self.data['bonus']}D{self.data['delay']}"
        )

    @property
    def ready(self):
        return sum([r.status is RequestStatus.ACCEPTED for r in self.joined.values()]) == self.players_num

    def join_player(self, player: User, data: dict):
        status = RequestStatus.JOINED if data == self.data else RequestStatus.CHANGED
        join_request = JoinRequest(data, status)

        self.joined[player] = join_request

        return self.ready

    def accept_player(self, player: User):
        join_request = self.joined.get(player)

        if join_request.data != self.data:
            raise JoinRequestError("Data not equal")

        join_request.status = RequestStatus.ACCEPTED

    def change_data(self, new_data: dict):
        if self.data != new_data:
            self.data = new_data

            to_return = []
            for player, join_request in self.joined.items():
                if join_request.data != self.data:
                    join_request.status = RequestStatus.RETURNED
                    to_return.append(player.ws)

            return to_return

    def remove_player(self, player: User):
        self.joined.pop(player)

    async def send_all(self, message: str):
        return asyncio.gather(*[user.send(message) for user in self.joined])
