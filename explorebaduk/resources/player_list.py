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
        asyncio.create_task(self._set_online())
        asyncio.create_task(self._set_offline())

    async def handle_request(self):
        await self.connect_ws()
        try:
            await self.handle_message()
        finally:
            await self.disconnect_ws()

    async def connect_ws(self):
        self.connected.add(self.ws)
        await self.player.add_ws(self.ws)
        await self.send_message({"status": "login", "player": self.player.as_dict()})

    async def handle_message(self):
        await self._refresh_list()
        while message := await self.receive_message():
            if message["action"] == "refresh":
                await self._refresh_list()

    async def disconnect_ws(self):
        self.connected.remove(self.ws)
        await self.player.remove_ws(self.ws)

    async def _set_online(self):
        await self.player.online_event.wait()
        self.app.players.add(self.player)
        await self.broadcast_message({"status": "online", "player": self.player.as_dict()})
        await self.player.online_event.clear()

    async def _set_offline(self):
        await self.player.offline_event.wait()
        self.app.players.remove(self.player)
        await self.broadcast_message({"status": "offline", "player": self.player.as_dict()})
        await self.player.offline_event.clear()

    async def _refresh_list(self):
        await asyncio.gather(
            *[
                self.send_message({"status": "online", "player": player.as_dict()})
                for player in self.app.players
                if self.ws not in player.ws_list
            ]
        )
