import asyncio

from explorebaduk.resources.websocket_view import WebSocketView
from explorebaduk.resources.explorebaduk import ExploreBadukPlayers
from explorebaduk.mixins import DatabaseMixin
from explorebaduk.models.player import Player


class PlayersFeedView(WebSocketView, ExploreBadukPlayers, DatabaseMixin):
    connected = set()

    def __init__(self, request, ws):
        super().__init__(request, ws)
        self.player = Player(self.ws, self.get_player_by_token(request))

    async def handle_request(self):
        await self.set_online()
        try:
            await self.handle_message()
        finally:
            await self.set_offline()

    async def handle_message(self):
        await self._refresh_list()
        while message := await self.receive_message():
            if message["action"] == "refresh":
                await self._refresh_list()

    async def set_online(self):
        self.connected.add(self.ws)

        if self.player.authorized:
            self.players.add(self.player)
            await self.broadcast_message({"status": "online", "player": self.player.as_dict()})

        await self.send_message({"status": "login", "player": self.player.as_dict()})

    async def set_offline(self):
        self.connected.remove(self.ws)

        if self.player.authorized:
            self.players.remove(self.player)
            await self.broadcast_message({"status": "offline", "player": self.player.as_dict()})

    async def _refresh_list(self):
        await asyncio.gather(
            *[
                self.send_message({"status": "online", "player": player.as_dict()})
                for player in self.players
                if player.ws is not self.ws
            ]
        )
