import asyncio
from typing import Set, Type

from sanic.log import logger
from sanic.request import Request
from websockets import WebSocketCommonProtocol

from explorebaduk.app import ExploreBadukApp

from .observer import Observer


class Feed:
    observer_class: Type[Observer] = Observer
    feed_name: str = NotImplemented

    def __init__(self, request: Request, ws: WebSocketCommonProtocol, **kwargs):
        self.request = request
        self.ws = ws
        self.conn = self.observer_class(request, ws)

    @property
    def app(self) -> ExploreBadukApp:
        """Sanic application"""
        return self.request.app

    @property
    def observers(self) -> Set[Observer]:
        """Connections related to feed"""
        return self.app.feeds[self.feed_name]

    def get_user_connections(self, user_id: int = None):

        if user_id := user_id or self.conn.user_id:
            return {conn for conn in self.observers if conn.user_id == user_id}

        return {self.conn}

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

    async def notify_all(self, event: str, data: dict, feed_name: str = None):
        """Sends message in JSON format to all observers

        :param event: event name
        :param data: event data
        :param feed_name: name of the feed
        """
        observers = self.app.feeds[feed_name] if feed_name else self.observers

        if observers:
            await asyncio.gather(*[conn.send(event, data) for conn in observers])
            logger.info("> [broadcast] [%s] %s", event, data)

    async def notify_user(self, event: str, data: dict, user_id: int = None):
        """Sends message to all observers with matching user_id

        :param event: event name
        :param data: event data
        :param user_id: user id
        """
        ws_list = self.get_user_connections(user_id)

        if ws_list:
            await asyncio.gather(*[conn.send(event, data) for conn in ws_list])
        else:
            error_message = {"message": f"User with {user_id=} not connected to the feed {self.feed_name}"}
            await self.conn.send("error", error_message)
