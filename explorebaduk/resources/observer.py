from typing import Optional

import simplejson as json
from sanic.log import logger
from sanic.request import Request
from websockets import WebSocketCommonProtocol

from explorebaduk.helpers import get_user_by_token
from explorebaduk.models import UserModel


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

    @property
    def username(self):
        if self.user:
            return self.user.username
        return "guest"

    async def authorize(self, token):
        if self.authorized:
            return await self.send("error", {"message": "Already authorized"})

        self.user = get_user_by_token(self.request, token)
        await self.send("auth.whoami", self.user.as_dict() if self.user else None)

        return self.authorized

    async def _send(self, message: str):
        await self.ws.send(message)

    async def send(self, event: str, data: dict):
        await self._send(json.dumps({"event": event, "data": data}))
        logger.info("> [%s:%s] %s", self.username, event, data)

    async def receive(self):
        message = {}
        data = await self.ws.recv()
        try:
            message = json.loads(data)
        except json.JSONDecodeError as ex:
            await self.send("error", {"message": str(ex), "data": data})
        return message.get("event"), message.get("data")
