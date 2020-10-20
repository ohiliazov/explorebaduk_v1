import asyncio

from explorebaduk.resources.websocket_view import WebSocketView
from explorebaduk.mixins import DatabaseMixin
from explorebaduk.models import Player


class PlayersFeedView(WebSocketView, DatabaseMixin):
    connected = set()

    def __init__(self, request, ws):
        super().__init__(request, ws)

        self.player = self._get_player()

    @property
    def excluded(self) -> set:
        return self.player.ws_list

    def _get_player(self):
        if user := self.get_user_by_token(self.request):
            for player in self.app.players:
                if user.user_id == player.user_id:
                    return player
            return Player(user)
        return Player()

    async def handle_request(self):
        await self.connect_ws()
        try:
            await self._send_player_list()
            await self.handle_message()
        finally:
            await self.disconnect_ws()

    async def connect_ws(self):
        self.connected.add(self.ws)

        async with self.player.lock:
            self.player.subscribe(self.ws)
            self.app.players.add(self.player)

            if self.player.authorized:
                await self._send_login_info()

                if len(self.player.ws_list) == 1:
                    await self._broadcast_online()

    async def disconnect_ws(self):
        self.connected.remove(self.ws)
        async with self.player.lock:
            self.player.unsubscribe(self.ws)
            if not self.player.ws_list:
                self.app.players.remove(self.player)

                if self.player.authorized:
                    await self._broadcast_offline()

    async def handle_message(self):
        while message := await self.receive_message():
            if message["action"] == "refresh":
                await self._send_player_list()

    async def _send_login_info(self):
        await self.send_message({"status": "login", "user": self.player.as_dict()})

    async def _broadcast_online(self):
        await self.broadcast_message({"status": "online", "player": self.player.as_dict()})

    async def _broadcast_offline(self):
        await self.broadcast_message({"status": "offline", "player": self.player.as_dict()})

    async def _send_player_list(self):
        await asyncio.gather(
            *[
                self.send_message({"status": "online", "player": player.as_dict()})
                for player in self.app.players
                if player.authorized
            ]
        )
