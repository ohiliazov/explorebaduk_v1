import logging

from fastapi import WebSocket

from explorebaduk.broadcast import broadcast
from explorebaduk.database import DatabaseHandler, Session
from explorebaduk.dependencies import get_current_user
from explorebaduk.messages import Message, ReceivedMessage, WhoAmIMessage

logger = logging.getLogger("explorebaduk")


class ConnectionManager:
    def __init__(self, websocket: WebSocket, session: Session):
        self.websocket = websocket
        self.db = DatabaseHandler(session)
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
        await self.websocket.send_json(message.json())
        logger.info("[%s] > %s", self.username, str(message))

    async def initialize(self):
        await self.websocket.accept()
        message = await self.websocket.receive_text()
        self.user = get_current_user(message, self.db)

        await self._send(WhoAmIMessage(self.user))

    async def send_messages(self):
        raise NotImplementedError

    async def finalize(self):
        raise NotImplementedError

    async def start_sender(self, channel: str):
        async with broadcast.subscribe(channel=channel) as subscriber:
            async for event in subscriber:
                message = ReceivedMessage(event.message)
                await self.websocket.send_json(message.json())

    async def start_receiver(self):
        async for message in self.websocket.iter_text():
            logger.debug(f"< {message}")
