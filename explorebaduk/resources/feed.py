import asyncio
import json
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
        self.connected.add(self.ws)

    async def run(self):
        pass

    async def finalize(self):
        self.connected.remove(self.ws)

    async def receive_message(self):
        message = await self.ws.recv()
        logger.info("< %s", message)
        return message

    async def send_message(self, data: dict):
        message = json.dumps(data)
        await self.ws.send(message)
        logger.info("> %s", message)

    @classmethod
    async def broadcast_message(cls, data: dict):
        message = json.dumps(data)
        if cls.connected:
            await asyncio.gather(*[ws.send(message) for ws in cls.connected])
            logger.info("@ %s", message)
