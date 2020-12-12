import asyncio

import simplejson as json
from sanic.log import logger
from sanic.request import Request
from websockets import WebSocketCommonProtocol

from explorebaduk.mixins import Subscriber


class BaseFeed:
    def __init__(self, request: Request, ws: WebSocketCommonProtocol, **kwargs):
        self.request = request
        self.ws = ws
        self.conn = Subscriber(request, ws)

    @property
    def app(self):
        return self.request.app

    @property
    def connected(self) -> set:
        return set()

    @classmethod
    def as_view(cls):
        async def wrapper(request, ws, **kwargs):
            await cls(request, ws, **kwargs).run()

        return wrapper

    async def connect(self):
        pass

    async def run(self):
        pass

    async def disconnect(self):
        pass

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

    async def broadcast_message(self, data: dict):
        message = json.dumps(data)

        if self.connected:
            await asyncio.gather(*[conn.send(message) for conn in self.connected if conn != self.conn])
            logger.info("> [broadcast_message] %s", message)

    async def send_event(self, event: str, data: dict):
        logger.info("> [%s] %s", event, data)
        await self.send_message({"event": event, "data": data})

    async def broadcast_event(self, event: str, data: dict):
        logger.info("> [%s] %s", event, data)

        if self.connected:
            await asyncio.gather(*[conn.send(event, data) for conn in self.connected])
            logger.info("> [%s] %s", event, data)
