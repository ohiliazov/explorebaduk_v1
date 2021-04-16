import logging

from fastapi import WebSocket, WebSocketDisconnect
from fastapi.concurrency import run_until_first_complete
from fastapi.routing import APIRouter

from explorebaduk.broadcast import broadcast
from explorebaduk.crud import get_user_by_token
from explorebaduk.messages import Message, ReceivedMessage, WhoAmIMessage
from explorebaduk.shared import GameRequests, UsersOnline

logger = logging.getLogger("explorebaduk")
router = APIRouter()


class Connection:
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.user = None

    async def __aiter__(self):
        async for message in self.websocket.iter_text():
            yield ReceivedMessage.from_string(message)

    @property
    def username(self):
        return self.user.username if self.user else "guest"

    async def _recv(self) -> ReceivedMessage:
        message = ReceivedMessage.from_string(await self.websocket.receive_text())
        logger.info("[%s] < %s", self.username, str(message))
        return message

    async def _send(self, message: Message):
        await self.websocket.send_json(message.json())
        logger.info("[%s] > %s", self.username, str(message))

    async def initialize(self):
        await self.websocket.accept()
        message = await self.websocket.receive_text()

        if user := get_user_by_token(message):
            self.user = user
            await UsersOnline.add(self.user, self.websocket)

        await self._send(WhoAmIMessage(self.user))

    async def finalize(self):
        if self.user:
            await UsersOnline.remove(self.user, self.websocket)

            if not UsersOnline.is_online(self.user):
                await GameRequests.remove_open_game(self.user)
                await GameRequests.clear_direct_invites(self.user)


@router.websocket_route("/ws")
async def ws_handler(websocket: WebSocket):
    connection = Connection(websocket)
    try:
        await connection.initialize()

        tasks = [
            (ws_receiver, {"connection": connection}),
            (ws_sender, {"connection": connection}),
        ]
        if connection.user:
            tasks.append((user_ws_sender, {"connection": connection}))
        await run_until_first_complete(*tasks)
    except WebSocketDisconnect:
        pass
    finally:
        await connection.finalize()


async def ws_receiver(connection: Connection):
    async for message in connection:
        logger.debug(f"< {message}")


async def ws_sender(connection: Connection):
    async with broadcast.subscribe(channel="main") as subscriber:
        async for event in subscriber:
            message = ReceivedMessage(event.message)
            await connection.websocket.send_json(message.json())


async def user_ws_sender(connection: Connection):
    user_id = connection.user.user_id
    async with broadcast.subscribe(channel=f"user__{user_id}") as subscriber:
        async for event in subscriber:
            message = ReceivedMessage(event.message)
            await connection.websocket.send_json(message.json())
