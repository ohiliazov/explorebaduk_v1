import asyncio
import json
from sanic.log import logger

from explorebaduk.resources.v1.feeds import BaseFeed


def player_payload(user, status: str):
    return json.dumps({
        "user_id": user.user_id,
        "last_name": user.last_name,
        "first_name": user.first_name,
        "rating": user.rating,
        "status": status,
    })


def payload_user_online(user):
    return player_payload(user, "online")


def payload_user_offline(user):
    return player_payload(user, "offline")


class PlayerFeed(BaseFeed):

    @property
    def connected(self) -> set:
        return self.app.feeds["players"]

    async def setup_feed(self):
        if user := self.request.ctx.user:
            await self._spread_message(payload_user_online(user))
            self._add_player(user)

        self.connected.add(self.ws)

    async def run_feed(self):
        while True:
            await self._refresh_players()
            await self.ws.recv()

    async def teardown_feed(self):
        self.connected.remove(self.ws)

        if user := self._remove_player():
            await self._spread_message(payload_user_offline(user))

    async def _refresh_players(self):
        await asyncio.gather(*[self.ws.send(payload_user_online(user)) for user in self.app.players.values()])

    def _add_player(self, user):
        self.app.players[self.ws] = user

    def _remove_player(self):
        return self.app.players.pop(self.ws, None)

    async def _spread_message(self, message: str):
        if self.connected:
            await asyncio.gather(*[ws.send(message) for ws in self.connected])
            logger.info(message)
