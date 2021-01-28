from typing import Optional

import simplejson as json
from sanic.log import logger
from sanic.request import Request
from websockets import WebSocketCommonProtocol

from explorebaduk.crud import get_user_by_token
from explorebaduk.messages import ErrorMessage, Message, WhoAmIMessage
from explorebaduk.models import UserModel


class Connection:
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
        return "<guest>"

    async def authorize(self, token, online_user_ids: set):
        if self.authorized:
            await self.send_message(ErrorMessage("Already authorized"))

        if user := get_user_by_token(token):
            if user.user_id not in online_user_ids:
                self.user = user
                await self.send_message(WhoAmIMessage(self.user))
                return True
            else:
                await self.send_message(ErrorMessage("Already authorized from another device"))
        else:
            await self.send_message(ErrorMessage("Invalid or expired token provided"))
        return False

    async def _send(self, message: str):
        await self.ws.send(message)

    async def send(self, event: str, data: dict):
        await self._send(json.dumps({"event": event, "data": data}))
        logger.info("> [notify] [%s] [%s] %s", self.username, event, data)

    async def send_message(self, message: Message):
        await self.ws.send(str(message))

    async def receive(self):
        message = {}
        data = await self.ws.recv()
        try:
            message = json.loads(data)
        except json.JSONDecodeError as ex:
            await self.send("error", {"message": str(ex), "data": data})
        return message.get("event"), message.get("data")
