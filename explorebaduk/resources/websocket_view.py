import asyncio
import simplejson as json

from sanic.log import logger
from sanic.request import Request
from websockets import WebSocketCommonProtocol


class WebSocketView:
    def __init__(self, request: Request, ws: WebSocketCommonProtocol, **kwargs):
        self.request = request
        self.ws = ws

    @property
    def app(self):
        return self.request.app

    @property
    def connected(self) -> set:
        raise NotImplementedError

    async def handle_request(self):
        raise NotImplementedError

    @classmethod
    def as_view(cls):
        async def wrapper(request, ws, **kwargs):
            feed_handler = cls(request, ws, **kwargs)

            await feed_handler.handle_request()

        return wrapper

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
        logger.info("> [%s:%d] %s", *self.ws.remote_address[:2], message)

    async def broadcast_message(self, data: dict):
        message = json.dumps(data)

        if self.connected:
            await asyncio.gather(*[ws.send(message) for ws in self.connected])
            logger.info("> [broadcast] %s", message)
