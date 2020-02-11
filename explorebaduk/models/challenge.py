import asyncio

from typing import List

from explorebaduk.models.user import User
from explorebaduk.constants import RequestStatus
from explorebaduk.exceptions import JoinRequestError


class ChallengeData:
    def __init__(self, data: dict):
        # flags
        self.is_open = data["is_open"]
        self.undo = data["undo"]
        self.pause = data["pause"]

        # time system
        self.time_system = data['time_system'].value
        self.main_time = data['main_time']
        self.overtime = data['overtime']
        self.periods = data['periods']
        self.stones = data['stones']
        self.bonus = data['bonus']
        self.delay = data['delay']

    def __str__(self):
        return (
            f"FL[{self.is_open:d}{self.undo:d}{self.pause:d}]"
            f"TS[{self.time_system}M{self.main_time}"
            f"O{self.overtime}P{self.periods}S{self.stones}B{self.bonus}D{self.delay}]"
        )


class JoinRequest:
    def __init__(self, user: User, data: dict, status: RequestStatus, color: str = None):
        self.user = user
        self.data = ChallengeData(data)
        self.status = status
        self.color = color

    def join(self):
        self.status = RequestStatus.JOINED

    def accept(self):
        self.status = RequestStatus.ACCEPTED

    def set_color(self, color):
        assert color in {"black", "white", None}
        self.color = color


class Challenge:
    def __init__(self, challenge_id: int, creator: User, data: dict):

        self.id = challenge_id
        self.creator = creator
        self.blacklist = set()

        # game info
        self.name = data['name']
        self.game_type = data['game_type'].value
        self.rules = data['rules'].value
        self.width = data['width']
        self.height = data['height']
        self.rank_lower = data['rank_lower']
        self.rank_upper = data['rank_upper']

        self.data = ChallengeData(data)

        self.joined: List[JoinRequest] = [JoinRequest(creator, data, RequestStatus.ACCEPTED)]

    @property
    def board_size(self):
        return f"{self.width}:{self.height}"

    def __str__(self):
        """ Returns string representation of challenge
        ID[<game_id>]GN[<name>]
        GI[<game_type>R<rules>W<width>H<height>MIN<rank_lower>MAX<rank_upper]
        FL[<is_open><undo><pause>]
        TS[<time_system>M<main_time>O<overtime>P<periods>S<stones>B<bonus>D<delay>]
        """
        return (
            f"ID[{self.id}]GN[{self.name}]"
            f"GI[{self.game_type}R{self.rules}W{self.width}H{self.height}MIN{self.rank_lower}MAX{self.rank_upper}]"
            f"{self.data}"
        )


    @property
    def accepted_players(self):
        return [player for player in self.joined]

    @property
    def ready(self):
        return sum([r.status is RequestStatus.ACCEPTED for r in self.joined]) == 2

    def join_player(self, player: User, data: dict):
        join_request = [user for user in self.joined if user == player]

        if join_request:
            raise JoinRequestError("Already joined")

        request_data = ChallengeData(data)
        status = RequestStatus.JOINED if request_data == self.data else RequestStatus.CHANGED
        join_request = JoinRequest(player, data, status)

        self.joined.append(join_request)

        return self.ready

    def accept_player(self, player: User):
        join_request = [user for user in self.joined if user == player]

        if not join_request:
            raise JoinRequestError("Player not found")

        if join_request[0].data != self.data:
            raise JoinRequestError("Data not equal")

        join_request[0].status = RequestStatus.ACCEPTED

    def change_data(self, new_data: dict):
        if self.data != new_data:
            self.data = new_data

            to_return = []
            for join_request in self.joined:
                if join_request.data != self.data:
                    join_request.status = RequestStatus.RETURNED
                    to_return.append(join_request.user)

            return to_return

    def remove_player(self, player: User):
        join_request = [user for user in self.joined if user == player]

        if not join_request:
            raise JoinRequestError("Player not found")

        self.joined.remove(join_request[0])

    async def send_all(self, message: str):
        return asyncio.gather(*[j.user.ws.send(message) for j in self.joined])
