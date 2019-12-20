import json

from typing import Set, Dict, Optional

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


class Challenge:
    def __init__(self, creator, data: dict):
        self.creator = creator
        self.data = data
        self.joined: Dict[Player, str] = {creator: 'accepted'}
        self.blacklist = set()

    @property
    def ready(self):
        return list(self.joined.values()).count('accepted') == 2

    def join_player(self, player):
        if player not in self.blacklist:
            self.joined[player] = 'joined'

    def accept_player(self, player):
        if player not in self.blacklist:
            self.joined[player] = 'accepted'

    def return_player(self, player):
        if player not in self.blacklist:
            self.joined[player] = 'returned'

    def accept_edits(self, player):
        if player not in self.blacklist:
            self.joined[player] = 'accept_edits'

    def revise_edits(self, player):
        if player not in self.blacklist:
            self.joined[player] = 'revise_edits'

    def add_to_blacklist(self, player):
        self.blacklist.add(player)
        self.remove_player(player)

    def remove_player(self, player: Player):
        self.joined.pop(player)

    def to_dict(self):
        return {
            'data': self.data,
            'creator': self.creator.full_name,
            'joined': [{player.full_name: status} for player, status in self.joined.items()],
        }


class Game:
    def __init__(self, players: Set[Player] = None):
        self.players: Set[Player] = players or set()
        self.joined: Set[Player] = set()

    @property
    def players_joined(self):
        return all([player in self.joined for player in self.players])
