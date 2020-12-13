import asyncio
from typing import Optional, Set, Type

import simplejson as json
from sanic.log import logger
from sanic.request import Request
from websockets import WebSocketCommonProtocol

from explorebaduk.helpers import get_user_by_token
from explorebaduk.models.user import UserModel


class Observer:
    def __init__(self, request: Request, ws: WebSocketCommonProtocol):
        self.request = request
        self.ws = ws
        self.user: Optional[UserModel] = None
        self.data = {}

    @property
    def authorized(self):
        return self.user is not None

    @property
    def user_id(self):
        if self.user:
            return self.user.user_id

    def authorize(self, token):
        self.user = get_user_by_token(self.request, token)

        return self.authorized

    async def _send(self, message: str):
        await self.ws.send(message)

    async def send(self, event: str, data: dict):
        await self._send(json.dumps({"event": event, "data": data}))
        logger.info("> [%s] %s", event, data)

    async def receive(self):
        message = json.loads(await self.ws.recv())
        return message["event"], message.get("data")


class Subject:
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
                await view.run()
            finally:
                view.observers.remove(view.conn)
                await view.disconnect()

        return wrapper

    async def run(self):
        raise NotImplementedError()

    async def disconnect(self):
        raise NotImplementedError()

    async def broadcast(self, event: str, data: dict):
        if self.observers:
            await asyncio.gather(*[conn.send(event, data) for conn in self.observers])
            logger.info("> [broadcast] [%s] %s", event, data)
