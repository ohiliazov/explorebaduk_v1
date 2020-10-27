import asyncio
import simplejson as json
from typing import Type
from sanic.log import logger
from sanic.request import Request
from websockets import WebSocketCommonProtocol

from explorebaduk.helpers import get_user_by_token
from explorebaduk.mixins import Subscriber


class GlobalFeed:

    connected: set
    conn_class: Type[Subscriber]

    def __init__(self, request: Request, ws: WebSocketCommonProtocol, **kwargs):
        self.request = request
        self.ws = ws
        self.user = None
        self.conn = None

    @property
    def app(self):
        return self.request.app

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
        self.user = get_user_by_token(self.request)

        if user := get_user_by_token(self.request):
            self.user = user

            for conn in self.connections:
                if conn.user_id == self.user.user_id:
                    self.conn = conn

        if not self.conn:
            self.conn = self.conn_class(self.user)

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
            await asyncio.gather(*[ws.send(message) for ws in self.connected - self.excluded])
            logger.info("> [broadcast_message] %s", message)
