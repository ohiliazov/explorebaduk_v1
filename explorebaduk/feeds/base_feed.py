import asyncio
import simplejson as json
from typing import Type
from sanic.log import logger
from sanic.request import Request
from websockets import WebSocketCommonProtocol

from explorebaduk.helpers import get_user_by_token
from explorebaduk.mixins import Subscriber


class BaseFeed:
    conn_class: Type[Subscriber]

    def __init__(self, request: Request, ws: WebSocketCommonProtocol, **kwargs):
        self.request = request
        self.ws = ws
        self.user = get_user_by_token(self.request)
        self.conn = None

    @property
    def app(self):
        return self.request.app

    async def receive_message(self):
        message = await self.ws.recv()
        logger.info("< [%s:%d] %s", *self.ws.remote_address[:2], message)
        try:
            return json.loads(message)
        except json.JSONDecodeError:
            return await self.send_message({"error": "Unexpected error"})

    async def send_message(self, data: dict):
        message = json.dumps(data)

        await self.ws.send(message)
        logger.info("> [send_message] %s", message)

    @staticmethod
    async def send_messages(ws_list, data: dict):
        message = json.dumps(data)

        if ws_list:
            await asyncio.gather(*[ws.send(message) for ws in ws_list])
            logger.info("> [send_messages] %s", message)
