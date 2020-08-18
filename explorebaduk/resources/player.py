from sanic import response
from sanic.views import HTTPMethodView
from sanic.request import Request

import asyncio

from explorebaduk.resources.feed import WebSocketFeed


class PlayerStatus:
    ONLINE = "online"
    OFFLINE = "offline"


def player_online(user) -> dict:
    return {"status": PlayerStatus.ONLINE, **user.as_dict()}


def player_offline(user) -> dict:
    return {"status": PlayerStatus.OFFLINE, **user.as_dict()}


class PlayerView(HTTPMethodView):
    """View to get player card"""

    async def get(self, request: Request, player_id: str):
        if user := request.app.db.select_user(int(player_id)):
            return response.json(user.as_dict())

        return response.json({"message": "User not found"}, 404)


class PlayersFeed(WebSocketFeed):
    connected = set()

    @property
    def players(self):
        return self.app.players

    @property
    def user(self):
        return self.request.ctx.user

    async def initialize(self):
        await self._set_online()
        await super().initialize()

    async def run(self):
        await self.send_players_list()
        while message := await self.receive_message():
            if message == "refresh":
                await self.send_players_list()

    async def finalize(self):
        await super().finalize()
        await self._set_offline()

    async def send_players_list(self):
        await asyncio.gather(*[self.send_message(player_online(user)) for user in self.players.values()])

    async def _set_online(self):
        if self.user and self.user not in self.players.values():
            await self.broadcast_message(player_online(self.user))
            self.players[self.ws] = self.user

    async def _set_offline(self):
        if self.user:
            await self.broadcast_message(player_offline(self.user))
            self.players.pop(self.ws, None)
