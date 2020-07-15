import asyncio
from typing import Set
from sanic.log import logger
from sanic.request import Request
from websockets import WebSocketClientProtocol


class WebSocketFeed:
    connected: Set = NotImplemented

    def __init__(self, request: Request, ws: WebSocketClientProtocol):
        self.request = request
        self.ws = ws

    @property
    def app(self):
        return self.request.app

    @classmethod
    def as_feed(cls):

        async def wrapper(request, ws):
            feed_handler = cls(request, ws)

            await feed_handler.initialize()
            try:
                await feed_handler.run()
            finally:
                await feed_handler.finalize()

        return wrapper

    async def initialize(self):
        pass

    async def run(self):
        pass

    async def finalize(self):
        pass

    async def broadcast(self, message: str):
        if self.connected:
            await asyncio.gather(*[ws.send(message) for ws in self.connected])
            logger.info(message)
