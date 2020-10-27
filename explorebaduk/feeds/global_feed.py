import asyncio
import simplejson as json

from sanic.log import logger

from .base_feed import BaseFeed


class GlobalFeed(BaseFeed):
    connected: set

    @property
    def excluded(self) -> set:
        return set()

    @property
    def connections(self) -> set:
        raise NotImplementedError

    @classmethod
    def as_view(cls):
        async def wrapper(request, ws, **kwargs):
            feed_handler = cls(request, ws, **kwargs)
            feed_handler._initialize()

            feed_handler.connected.add(ws)
            await feed_handler.connect_ws()
            try:
                await feed_handler.handle_request()
            finally:
                feed_handler.connected.remove(ws)
                await feed_handler.disconnect_ws()

        return wrapper

    async def connect_ws(self):
        pass

    async def handle_request(self):
        pass

    async def disconnect_ws(self):
        pass

    def _initialize(self):
        if self.user:
            for conn in self.connections:
                if conn.user_id == self.user.user_id:
                    self.conn = conn

        if not self.conn:
            self.conn = self.conn_class(self.user)

    async def broadcast_message(self, data: dict):
        message = json.dumps(data)

        if self.connected:
            await asyncio.gather(*[ws.send(message) for ws in self.connected - self.excluded])
            logger.info("> [broadcast_message] %s", message)
