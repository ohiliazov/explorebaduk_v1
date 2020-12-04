import asyncio
from typing import Type

import simplejson as json
from sanic.log import logger
from sanic.request import Request
from websockets import WebSocketCommonProtocol

from explorebaduk.helpers import get_user_by_token
from explorebaduk.mixins import Subscriber


class BaseFeed:
    conn_class: Type[Subscriber]

    def __init__(self, request: Request, ws: WebSocketCommonProtocol, **kwargs):
        self.request = request
        self.ws = ws
        self.user = get_user_by_token(self.request)
        self.conn = None

    @property
    def app(self):
        return self.request.app

    @property
    def connected(self) -> set:
        return set()

    def _setup_connection(self):
        if self.user:
            for conn in self.connected:
                if conn.user_id == self.user.user_id:
                    self.conn = conn

        if not self.conn:
            self.conn = self.conn_class(self.user)
            self.connected.add(self.conn)

    @classmethod
    def as_view(cls):
        async def wrapper(request, ws, **kwargs):
            feed_handler = cls(request, ws, **kwargs)
            feed_handler._setup_connection()

            await feed_handler.connect()
            try:
                await feed_handler.run()
            finally:
                await feed_handler.disconnect()

        return wrapper

    async def connect(self):
        pass

    async def run(self):
        pass

    async def disconnect(self):
        pass

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
            await asyncio.gather(*[conn.send(message) for conn in self.connected if conn != self.conn])
            logger.info("> [broadcast_message] %s", message)

    async def send_event(self, event: str, data: dict):
        logger.info("> [%s] %s", event, data)
        await self.send_message({"event": event, "data": data})

    async def broadcast_event(self, event: str, data: dict):
        logger.info("> [%s] %s", event, data)
        await self.broadcast_message({"event": event, "data": data})
