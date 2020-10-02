import asyncio

from explorebaduk.resources.websocket_view import WebSocketView
from explorebaduk.mixins import DatabaseMixin
from explorebaduk.models import Player


class PlayersFeedView(WebSocketView, DatabaseMixin):
    connected = set()

    def __init__(self, request, ws):
        super().__init__(request, ws)

        self.player = self._get_player()
        self._task = None

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
            await self._refresh_list()
            await self.handle_message()
        finally:
            await self.disconnect_ws()

    async def connect_ws(self):
        self.connected.add(self.ws)
        self.player.add_ws(self.ws)
        await self.send_message({"status": "login", "player": self.player.as_dict()})

        if self.player.authorized and self.player not in self.app.players:
            self.app.players.add(self.player)
            await self.broadcast_message(
                {"status": "online", "player": self.player.as_dict()},
                exclude_ws=self.player.ws_list,
            )

            # TODO: make proper finish
            self._task = asyncio.create_task(self._set_offline())

    async def handle_message(self):
        while message := await self.receive_message():
            if message["action"] == "refresh":
                await self._refresh_list()

    async def disconnect_ws(self):
        self.connected.remove(self.ws)
        self.player.remove_ws(self.ws)

    async def _set_offline(self):
        await self.player.wait_offline()
        self.app.players.remove(self.player)
        await self.broadcast_message(
            {"status": "offline", "player": self.player.as_dict()},
            exclude_ws=self.player.ws_list,
        )

    async def _refresh_list(self):
        await asyncio.gather(
            *[
                self.send_message({"status": "online", "player": player.as_dict()})
                for player in self.app.players
                if self.ws not in player.ws_list
            ]
        )
