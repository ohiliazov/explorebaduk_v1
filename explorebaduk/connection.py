from fastapi import WebSocket

from explorebaduk.broadcast import broadcast
from explorebaduk.database import DatabaseHandler
from explorebaduk.dependencies import parse_token
from explorebaduk.logger import logger
from explorebaduk.messages import Message, ReceivedMessage, WhoAmIMessage


class ConnectionManager:
    def __init__(self, websocket: WebSocket, db: DatabaseHandler):
        self.websocket = websocket
        self.db = db
        self.user = None

    async def __aiter__(self):
        async for message in self.websocket.iter_text():
            yield ReceivedMessage.from_string(message)

    @property
    def user_id(self):
        if self.user:
            return self.user.user_id

    @property
    def username(self):
        return self.user.username if self.user else "guest"

    async def _send(self, message: Message):
        logger.info("[%s] > %s", self.username, str(message))
        await self.websocket.send_json(message.json())

    async def initialize(self):
        await self.websocket.accept()
        message = await self.websocket.receive_text()
        if email := parse_token(message):
            self.user = self.db.get_user_by_email(email)

        await self._send(WhoAmIMessage(self.user))

    async def send_messages(self):
        raise NotImplementedError

    async def finalize(self):
        raise NotImplementedError

    async def start_sender(self, channel: str):
        async with broadcast.subscribe(channel=channel) as subscriber:
            async for event in subscriber:
                await self._send(ReceivedMessage(event.message))

    async def start_receiver(self):
        async for message in self.websocket.iter_text():
            logger.debug(f"< {message}")
