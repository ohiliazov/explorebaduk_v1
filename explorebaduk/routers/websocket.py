import logging

from fastapi import WebSocket, WebSocketDisconnect
from fastapi.concurrency import run_until_first_complete
from fastapi.routing import APIRouter

from explorebaduk.broadcast import broadcast
from explorebaduk.crud import get_players_list, get_user_by_token
from explorebaduk.messages import (
    Message,
    PlayerListMessage,
    PlayersAddMessage,
    PlayersRemoveMessage,
    ReceivedMessage,
    WhoAmIMessage,
)

logger = logging.getLogger("uvicorn")
router = APIRouter()


class ConnectionStatus:
    ONLINE = "online"
    PLAYING = "playing"


class Connection:
    users_online = set()

    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.user = None

    async def __aiter__(self):
        async for message in self.websocket.iter_text():
            yield ReceivedMessage.from_string(message)

    async def _recv(self) -> ReceivedMessage:
        message = ReceivedMessage.from_string(await self.websocket.receive_text())
        logger.info(
            '%s - "WebSocket %s" [recv] %s',
            self.websocket.scope["client"],
            self.websocket.scope["root_path"] + self.websocket.scope["path"],
            str(message),
        )
        return message

    async def _send(self, message: Message):
        logger.info(
            '%s - "WebSocket %s" [send] %s',
            self.websocket.scope["client"],
            self.websocket.scope["root_path"] + self.websocket.scope["path"],
            str(message),
        )
        await self.websocket.send_json(message.json())

    async def initialize(self):
        await self.websocket.accept()
        message = await self._recv()

        if message.event == "authorize":
            if user := get_user_by_token(message.data):
                if user.user_id not in self.users_online:
                    self.user = user
                    self.users_online.add(user.user_id)
                    await broadcast.publish("main", PlayersAddMessage(user).json())

        await self._send(WhoAmIMessage(self.user))
        await self.send_player_list()

    async def finalize(self):
        if self.user:
            self.users_online.remove(self.user.user_id)
            await broadcast.publish("main", PlayersRemoveMessage(self.user).json())
        logger.info(
            '%s - "WebSocket %s" [closed]',
            self.websocket.scope["client"],
            self.websocket.scope["root_path"] + self.websocket.scope["path"],
        )

    async def send_player_list(self, search_string: str = None):
        user_ids = self.users_online.copy()
        if self.user:
            user_ids.remove(self.user.user_id)

        player_list = get_players_list(user_ids, search_string)
        await self._send(PlayerListMessage(player_list, self.user))

    async def send_player_add(self, message: ReceivedMessage):
        if self.user:
            message.data["friend"] = self.user.is_friend(message.data["user_id"])
        else:
            message.data["friend"] = False

        await self._send(message)


@router.websocket_route("/ws")
async def ws_handler(websocket: WebSocket):
    connection = Connection(websocket)
    try:
        await connection.initialize()
        await run_until_first_complete(
            (ws_receiver, {"connection": connection}),
            (ws_sender, {"connection": connection}),
        )
    except WebSocketDisconnect:
        pass
    finally:
        await connection.finalize()


async def ws_receiver(connection: Connection):
    async for message in connection:
        if message.event == "players.list":
            await connection.send_player_list(message.data)


async def ws_sender(connection: Connection):
    async with broadcast.subscribe(channel="main") as subscriber:
        async for event in subscriber:
            message = ReceivedMessage(event.message)
            if message.event == "players.add":
                await connection.send_player_add(message)
            else:
                await connection.websocket.send_json(message.json())
