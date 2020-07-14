import abc
from typing import Set
import asyncio
from asyncio import CancelledError
from sanic.log import logger
from sanic.request import Request
from websockets import WebSocketClientProtocol, ConnectionClosed


class BaseFeed(abc.ABC):
    def __init__(self, request: Request, ws: WebSocketClientProtocol):
        self.request = request
        self.ws = ws

    @abc.abstractmethod
    async def setup_feed(self):
        pass

    @abc.abstractmethod
    async def run_feed(self):
        pass

    @abc.abstractmethod
    async def teardown_feed(self):
        pass

    @classmethod
    def as_feed(cls):
        async def feed(request, ws):
            handler = cls(request, ws)

            await handler.setup_feed()
            try:
                await handler.run_feed()
            finally:
                await handler.teardown_feed()

        return feed

    @property
    def app(self):
        return self.request.app
