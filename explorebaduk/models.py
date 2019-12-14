from typing import Set, Dict, Optional

from explorebaduk.database import UserModel


class Player:
    def __init__(self):
        self.user: Optional[UserModel] = None
        self.created_challenges: Set[Challenge] = set()
        self.joined_challenges: Set[Challenge] = set()
        self.joined_games: Set[Game] = set()

    @property
    def logged_in(self):
        return self.user is not None

    def login_as(self, user: UserModel):
        self.user = user

    def logout(self):
        self.user = None

    def join_challenge(self, challenge: 'Challenge', status: str):
        self.joined_challenges.add(challenge)
        challenge.joined[self] = status

    def leave_challenge(self, challenge: 'Challenge'):
        self.joined_challenges.remove(challenge)
        challenge.joined.pop(self)


class Challenge:
    def __init__(self, creator: Player, data: dict):
        self.creator = creator
        self.data = data
        self.joined: Dict[Player] = {}
        self.blacklist = set()

    @property
    def ready(self):
        return list(self.joined.values()).count('accepted') == 1

    def cancel(self):
        for player in self.joined:
            player.leave_challenge(self)

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
        player.joined_challenges.remove(self)

    def to_dict(self):
        return {
            'data': self.data,
            'creator': self.creator.user.full_name,
            'joined': self.joined,
        }


class Game:
    def __init__(self, players: Set[Player] = None):
        self.players: Set[Player] = players or set()
        self.joined: Set[Player] = set()

    @property
    def players_joined(self):
        return all([player in self.joined for player in self.players])
