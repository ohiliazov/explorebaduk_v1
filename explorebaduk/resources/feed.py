import asyncio
from typing import Set, Type

from sanic import Sanic
from sanic.log import logger
from sanic.request import Request
from websockets import WebSocketCommonProtocol

from .observer import Observer


class Feed:
    observer_class: Type[Observer] = Observer

    def __init__(self, request: Request, ws: WebSocketCommonProtocol, **kwargs):
        self.request = request
        self.ws = ws
        self.conn = self.observer_class(request, ws)

    @property
    def app(self) -> Sanic:
        """Sanic application"""
        return self.request.app

    @property
    def observers(self) -> Set[Observer]:
        """Connections related to feed"""
        return set()

    @property
    def handlers(self) -> dict:
        """Message handlers"""
        return {}

    @classmethod
    def as_view(cls):
        async def wrapper(request, ws, **kwargs):
            view = cls(request, ws, **kwargs)
            view.observers.add(view.conn)
            try:
                await view.initialize()
                await view.run()
            except Exception as ex:
                logger.exception(str(ex))
            finally:
                view.observers.remove(view.conn)
                await view.finalize()

        return wrapper

    async def run(self):
        """Handles messages from connections"""
        while True:
            event, data = await self.conn.receive()

            if handler := self.handlers.get(event):
                await handler(data)

    async def initialize(self):
        """Initializes connection"""
        pass

    async def finalize(self):
        """Finalizes connection"""
        pass

    async def broadcast(self, event: str, data: dict):
        """Sends message in JSON format to all observers

        :param event: event name
        :param data: event data
        """
        if self.observers:
            await asyncio.gather(*[conn.send(event, data) for conn in self.observers])
            logger.info("> [broadcast] [%s] %s", event, data)
