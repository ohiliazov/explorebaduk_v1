from typing import Set, Optional

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

    def join_game(self, game: 'Game'):
        self.joined_games.add(game)
        game.join_player(self)

    def leave_game(self, game: 'Game'):
        self.joined_games.remove(game)
        game.leave_player(self)

    def join_challenge(self, challenge: 'Challenge'):
        self.joined_challenges.add(challenge)
        challenge.join_player(self)

    def leave_challenge(self, challenge: 'Challenge'):
        self.joined_challenges.remove(challenge)
        challenge.leave_player(self)


class Challenge:
    def __init__(self, creator: Player):
        self.creator = creator
        self.joined: Set[Player] = set()

    def join_player(self, player: Player):
        self.joined.add(player)

    def leave_player(self, player: Player):
        self.joined.remove(player)


class Game:
    def __init__(self, players: Set[Player] = None):
        self.players: Set[Player] = players or set()
        self.joined: Set[Player] = set()

    @property
    def players_joined(self):
        return all([player in self.joined for player in self.players])

    def join_player(self, player: Player):
        self.joined.add(player)

    def leave_player(self, player: Player):
        self.joined.remove(player)
