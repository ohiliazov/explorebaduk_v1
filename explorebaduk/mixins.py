import asyncio

import simplejson as json
from sanic.log import logger
from websockets import WebSocketCommonProtocol

from explorebaduk.models import UserModel


class Subscriber:
    def __init__(self, user: UserModel = None):
        self.user = user
        self._ws_list = set()
        self.lock = asyncio.Lock()

    @property
    def ws_list(self):
        return self._ws_list

    @property
    def user_id(self):
        if self.user:
            return self.user.user_id

    @property
    def authorized(self):
        return self.user is not None

    def subscribe(self, ws: WebSocketCommonProtocol):
        self._ws_list.add(ws)

    def unsubscribe(self, ws: WebSocketCommonProtocol):
        self._ws_list.remove(ws)

    async def send(self, message: str):
        if self._ws_list:
            await asyncio.gather(*[ws.send(message) for ws in self._ws_list], return_exceptions=True)
            logger.info("> [send] %s", message)

    async def send_json(self, data: dict):
        await self.send(json.dumps(data))

    async def send_event(self, event: str, data: dict):
        await self.send_json({"event": event, "data": data})
