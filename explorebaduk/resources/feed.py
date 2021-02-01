import asyncio
from typing import Set, Type

from sanic.log import logger
from sanic.request import Request
from websockets import WebSocketCommonProtocol

from explorebaduk.app import ExploreBadukApp
from explorebaduk.messages import MessageBase

from .connection import Connection


class Feed:
    observer_class: Type[Connection] = Connection
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
    def observers(self) -> Set[Connection]:
        """Connections related to feed"""
        return self.app.feeds[self.feed_name]

    def get_online_user_ids(self) -> Set[int]:
        return {conn.user_id for conn in self.observers}

    def get_feed_connections(self, feed_name: str = None) -> Set[Connection]:
        """Returns set of all connections to the given feed

        :param feed_name: defaults to current class feed name
        """
        return self.app.feeds[feed_name or self.feed_name]

    def get_user_connections(self, user_id: int = None, feed_name: str = None) -> Set[Connection]:
        """Returns set of all user connections to the given feed

        :param user_id: defaults to current connection user_id
        :param feed_name: defaults to current class feed name
        """
        if user_id := user_id or self.conn.user_id:
            return {conn for conn in self.get_feed_connections(feed_name) if conn.user_id == user_id}

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
                await view.conn.initialize_connection(view.get_online_user_ids())
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
            logger.info("> [notify_all] [%s] [%s] %s", feed_name or self.feed_name, event, data)
            await asyncio.gather(*[conn.send(event, data) for conn in observers])

    async def notify_user(self, event: str, data: dict, user_id: int = None):
        """Sends message to all observers with matching user_id

        :param event: event name
        :param data: event data
        :param user_id: user id
        """
        ws_list = self.get_user_connections(user_id)

        if ws_list:
            await asyncio.gather(*[conn.send(event, data) for conn in ws_list])

    async def broadcast(self, message: MessageBase, feed_name: str = None):
        """Broadcasts JSON message

        :param message: message to send
        :param feed_name: name of the feed
        """
        observers = self.app.feeds[feed_name or self.feed_name]

        if observers:
            logger.info("> [broadcast] [%s] %s", self.conn.user_id, str(message))
            await asyncio.gather(*[conn.send_message(message) for conn in observers])
