import asyncio
import json
from sanic.log import logger

from explorebaduk.resources.feeds.base import WebSocketFeed


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


class PlayerFeed(WebSocketFeed):
    connected = set()
    players = set()

    @property
    def user(self):
        return self.request.ctx.user

    async def initialize(self):
        if self.user:
            await self.broadcast(payload_user_online(self.user))
            self.players.add(self.user)

        self.connected.add(self.ws)

    async def run(self):
        while True:
            await asyncio.gather(*[self.ws.send(payload_user_online(user)) for user in self.players])
            await self.ws.recv()

    async def finalize(self):
        self.connected.remove(self.ws)

        if self.user:
            self.players.remove(self.user)
            await self.broadcast(payload_user_offline(self.user))
