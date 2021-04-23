import asyncio
import logging

from fastapi import WebSocket, WebSocketDisconnect
from fastapi.concurrency import run_until_first_complete
from fastapi.routing import APIRouter

from explorebaduk.broadcast import broadcast
from explorebaduk.crud import DatabaseHandler
from explorebaduk.dependencies import get_current_user
from explorebaduk.managers import UsersManager
from explorebaduk.messages import (
    ChallengeCreatedMessage,
    Message,
    ReceivedMessage,
    WhoAmIMessage,
)

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

        with DatabaseHandler() as db:
            self.user = get_current_user(message, db)

        if self.user:
            await UsersManager.add(self.user, self.websocket)
            await self._send_direct_challenges()

        await self._send_messages()
        await self._send(WhoAmIMessage(self.user))

    async def _send_messages(self):
        with DatabaseHandler() as db:
            challenges = db.list_challenges()
        messages = [ChallengeCreatedMessage(challenge) for challenge in challenges]

        if messages:
            await asyncio.wait([self._send(message) for message in messages])

    async def _send_direct_challenges(self):
        messages = []
        with DatabaseHandler() as db:
            messages.extend(
                [
                    ChallengeCreatedMessage(challenge)
                    for challenge in db.list_incoming_challenges(self.user_id)
                ],
            )
            messages.extend(
                [
                    ChallengeCreatedMessage(challenge)
                    for challenge in db.list_outgoing_challenges(self.user_id)
                ],
            )

        if messages:
            await asyncio.wait([self._send(message) for message in messages])

    async def finalize(self):
        if self.user:
            await UsersManager.remove(self.user, self.websocket)

            if not UsersManager.is_online(self.user):
                pass


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
