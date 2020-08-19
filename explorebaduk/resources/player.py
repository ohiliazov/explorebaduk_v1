from sanic import response
from sanic.views import HTTPMethodView
from sanic.request import Request

import asyncio

from explorebaduk.resources.feed import WebSocketFeed


class PlayerStatus:
    ONLINE = "online"
    OFFLINE = "offline"


def player_online_payload(user) -> dict:
    return {"status": PlayerStatus.ONLINE, "user": user.as_dict()}


def player_offline_payload(user) -> dict:
    return {"status": PlayerStatus.OFFLINE, "user": user.as_dict()}


class PlayerView(HTTPMethodView):
    """View to get player card"""

    async def get(self, request: Request, player_id: str):
        if user := request.app.db.select_user(int(player_id)):
            return response.json(user.as_dict())

        return response.json({"message": "User not found"}, 404)


class PlayersFeed(WebSocketFeed):

    @property
    def players(self):
        return self.app.players

    @property
    def connected(self) -> set:
        return set(self.players)

    @property
    def user(self):
        return self.request.ctx.user

    async def handle_request(self):
        await self.set_online()
        try:
            await self._send_players_list()
            await self.handle_message()
        finally:
            await self.set_offline()

    async def set_online(self):
        if self.user and self.user not in self.players.values():
            await self._send_player_online()

        self.players[self.ws] = self.user

    async def set_offline(self):
        self.players.pop(self.ws)

        if self.user and self.user not in self.players.values():
            await self._send_player_offline()

    async def handle_message(self):
        while message := await self.receive_message():
            if message == "refresh":
                await self._send_players_list()

    async def _send_players_list(self):
        await asyncio.gather(*[self.send_message(player_online_payload(user)) for user in set(self.players.values())])

    async def _send_player_online(self):
        message = player_online_payload(self.user)
        await self.broadcast_message(message)

    async def _send_player_offline(self):
        message = player_offline_payload(self.user)
        await self.broadcast_message(message)
