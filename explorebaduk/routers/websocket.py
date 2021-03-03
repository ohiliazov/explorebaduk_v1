import asyncio
import logging

from fastapi import WebSocket, WebSocketDisconnect
from fastapi.concurrency import run_until_first_complete
from fastapi.routing import APIRouter

from explorebaduk.broadcast import broadcast
from explorebaduk.crud import get_players_list, get_user_by_token
from explorebaduk.messages import (
    DirectInviteCancelledMessage,
    DirectInvitesMessage,
    Message,
    OpenGameCancelledMessage,
    OpenGamesMessage,
    PlayerListMessage,
    PlayerOfflineMessage,
    PlayerOnlineMessage,
    ReceivedMessage,
    WhoAmIMessage,
)
from explorebaduk.shared import DIRECT_INVITES, OPEN_GAMES, USERS_ONLINE

logger = logging.getLogger("uvicorn")
router = APIRouter()


class Connection:
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.user = None

    async def __aiter__(self):
        async for message in self.websocket.iter_text():
            yield ReceivedMessage.from_string(message)

    def log_message(self, event: str, message: Message = ""):
        logger.info(
            '%s - "WebSocket %s" [%s] %s',
            self.websocket.scope.get("client"),
            event,
            self.websocket.scope["root_path"] + self.websocket.scope["path"],
            str(message),
        )

    async def _recv(self) -> ReceivedMessage:
        message = ReceivedMessage.from_string(await self.websocket.receive_text())
        self.log_message("recv", message)
        return message

    async def _send(self, message: Message):
        await self.websocket.send_json(message.json())
        self.log_message("send", message)

    async def initialize(self):
        await self.websocket.accept()
        message = await self._recv()

        if message.event == "authorize":
            if user := get_user_by_token(message.data):
                if user.user_id not in USERS_ONLINE:
                    self.user = user
                    USERS_ONLINE.add(user.user_id)
                    await broadcast.publish("main", PlayerOnlineMessage(user).json())

        await self._send(WhoAmIMessage(self.user))
        await asyncio.gather(
            self.send_player_list(),
            self.send_open_games(),
            self.send_direct_invites(),
        )

    async def finalize(self):
        if self.user:
            USERS_ONLINE.remove(self.user.user_id)
            await broadcast.publish("main", PlayerOfflineMessage(self.user).json())

            if OPEN_GAMES.pop(self.user.user_id, None):
                await broadcast.publish(
                    "main",
                    OpenGameCancelledMessage(self.user).json(),
                )

            await asyncio.wait(
                [
                    broadcast.publish(
                        f"user__{user_id}",
                        DirectInviteCancelledMessage(self.user).json(),
                    )
                    for user_id in DIRECT_INVITES.pop(self.user.user_id, {})
                ],
            )

        self.log_message("closed")

    async def send_player_list(self, search_string: str = None):
        user_ids = USERS_ONLINE.copy()
        if self.user:
            user_ids.remove(self.user.user_id)

        player_list = get_players_list(user_ids, search_string)
        await self._send(PlayerListMessage(player_list))

    async def send_open_games(self):
        await self._send(OpenGamesMessage(OPEN_GAMES))

    async def send_direct_invites(self):
        if self.user:
            await self._send(DirectInvitesMessage(DIRECT_INVITES[self.user.user_id]))


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
        if message.event == "players.list":
            await connection.send_player_list(message.data)
        elif message.event == "games.open.list":
            await connection.send_open_games()
        elif message.event == "games.direct.list":
            await connection.send_direct_invites()
        elif message.event == "refresh":
            await connection.send_player_list()
            await connection.send_open_games()
            await connection.send_direct_invites()


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
