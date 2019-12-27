from typing import Dict

from explorebaduk.models.player import Player

JOINED = 'joined'
ACCEPTED = 'accepted'


class Challenge:
    def __init__(self, creator_ws, data: dict):
        self.creator_ws = creator_ws
        self.data = data
        self.joined: Dict[Player, Dict[str, str]] = {creator_ws: {'status': ACCEPTED}}
        self.blacklist = set()

    @property
    def status(self):
        return {player: data['status'] for player, data in self.joined.items()}

    @property
    def ready(self):
        return list(self.status.values()).count(ACCEPTED) == 2

    def join_player(self, player: Player, data: dict):
        if player not in self.blacklist:
            status = 'joined'
            self.joined[player] = {
                'status': status,
                'data': data,
            }

    def accept_player(self, player: Player):
        if player not in self.blacklist:
            self.joined[player]['status'] = 'accepted'

    def remove_player(self, player: Player):
        self.joined.pop(player)

    #
    # def return_player(self, player):
    #     if player not in self.blacklist:
    #         self.joined[player] = 'returned'
    #
    # def accept_edits(self, player):
    #     if player not in self.blacklist:
    #         self.joined[player] = 'accept_edits'
    #
    # def revise_edits(self, player):
    #     if player not in self.blacklist:
    #         self.joined[player] = 'revise_edits'
    #
    # def add_to_blacklist(self, player):
    #     self.blacklist.add(player)
    #     self.remove_player(player)

    def to_dict(self):
        return {
            'data': self.data,
            'status': self.status,
        }
