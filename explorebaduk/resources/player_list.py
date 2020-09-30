import asyncio

from explorebaduk.resources.websocket_view import WebSocketView
from explorebaduk.mixins import DatabaseMixin, PlayersMixin
from explorebaduk.models import Player


class PlayersFeedView(WebSocketView, PlayersMixin, DatabaseMixin):
    connected = set()

    def __init__(self, request, ws):
        super().__init__(request, ws)

        player = self.get_player_by_token(request)
        self.player = self.get_player_by_model(player) or Player(player)

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
        self.player.add_ws(self.ws)

        if self.player.authorized:
            self.app.players.add(self.player)

            if len(self.player.ws_list) == 1:
                await self.broadcast_message({"status": "online", "player": self.player.as_dict()})

        await self.send_message({"status": "login", "player": self.player.as_dict()})

    async def set_offline(self):
        self.connected.remove(self.ws)
        self.player.remove_ws(self.ws)

        if not self.player.online:
            self.app.players.remove(self.player)
            self.player.exit_event.set()

            if self.player.authorized:
                await self.broadcast_message({"status": "offline", "player": self.player.as_dict()})

    async def _refresh_list(self):
        await asyncio.gather(
            *[
                self.send_message({"status": "online", "player": player.as_dict()})
                for player in self.app.players
                if self.ws not in player.ws_list
            ]
        )
