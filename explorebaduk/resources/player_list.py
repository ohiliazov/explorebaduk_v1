import asyncio

from explorebaduk.resources.websocket_view import WebSocketView
from explorebaduk.mixins import DatabaseMixin


class PlayerStatus:
    LOGIN = "login"
    ONLINE = "online"
    OFFLINE = "offline"


def player_login_payload(player) -> dict:
    return {"status": PlayerStatus.LOGIN, "player": player.as_dict() if player else None}


def player_online_payload(player) -> dict:
    return {"status": PlayerStatus.ONLINE, "player": player.as_dict()}


def player_offline_payload(player) -> dict:
    return {"status": PlayerStatus.OFFLINE, "player_id": player.user_id}


class PlayersFeedView(WebSocketView, DatabaseMixin):
    def __init__(self, request, ws):
        super().__init__(request, ws)
        self.player = self.get_player_by_token(request)

    @property
    def players(self):
        return self.app.players

    @property
    def connected(self) -> set:
        return set(self.players)

    async def handle_request(self):
        await self.set_online()
        try:
            await self.handle_message()
        finally:
            await self.set_offline()

    async def set_online(self):
        self.players[self.ws] = self.player
        if self.player:
            await self._send_player_online()

        await self.send_message(player_login_payload(self.player))

    async def set_offline(self):
        self.players.pop(self.ws)

        if self.player and self.player not in self.players.values():
            await self._send_player_offline()

    async def handle_message(self):
        await self._send_players_list()
        while message := await self.receive_message():
            if message["action"] == "refresh":
                await self._send_players_list()

    async def _send_players_list(self):
        await asyncio.gather(*[
            self.send_message(player_online_payload(player))
            for player in set(self.players.values())
            if player and player is not self.player
        ])

    async def _send_player_online(self):
        message = player_online_payload(self.player)
        await self.broadcast_message(message)

    async def _send_player_offline(self):
        message = player_offline_payload(self.player)
        await self.broadcast_message(message)
