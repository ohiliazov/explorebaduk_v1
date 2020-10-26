import asyncio

import simplejson as json
from sanic.log import logger
from websockets import WebSocketCommonProtocol

from explorebaduk.database import UserModel


class Subscriber:
    def __init__(self, user: UserModel = None):
        self._user = user
        self.ws_list = set()

    @property
    def user_id(self):
        return self._user.user_id

    @property
    def authorized(self):
        return self._user is not None

    def as_dict(self):
        if self._user:
            return self._user.as_dict()

    def is_online(self) -> bool:
        return bool(self.ws_list)

    def subscribe(self, ws: WebSocketCommonProtocol):
        self.ws_list.add(ws)

    def unsubscribe(self, ws: WebSocketCommonProtocol):
        self.ws_list.remove(ws)

    async def send_json(self, data: dict):
        message = json.dumps(data)

        if self.ws_list:
            await asyncio.gather(*[ws.send(message) for ws in self.ws_list], return_exceptions=True)
            logger.info("> [send_json] %s", message)
