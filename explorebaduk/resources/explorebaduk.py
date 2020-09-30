from explorebaduk.database import PlayerModel
from explorebaduk.models.player import Player


class PlayersMixin:
    def get_player_by_model(self, player: PlayerModel):
        for player_online in self.app.players:
            if player.user_id == player_online.player_id:
                return player_online
        return Player(player)


class ExploreBadukChallenges:
    challenges = set()


class ExploreBadukGames:
    games = {}
