import asyncio
from typing import Set, Type

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
    def app(self):
        return self.request.app

    @property
    def observers(self) -> Set[Observer]:
        return set()

    @classmethod
    def as_view(cls):
        async def wrapper(request, ws, **kwargs):
            view = cls(request, ws, **kwargs)
            view.observers.add(view.conn)
            try:
                await view.handle()
            except Exception as ex:
                logger.exception(str(ex))
            finally:
                view.observers.remove(view.conn)
                await view.disconnect()

        return wrapper

    async def handle(self):
        raise NotImplementedError()

    async def disconnect(self):
        raise NotImplementedError()

    async def broadcast(self, event: str, data: dict):
        if self.observers:
            await asyncio.gather(*[conn.send(event, data) for conn in self.observers])
            logger.info("> [broadcast] [%s] %s", event, data)
