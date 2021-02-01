import asyncio

from fastapi import WebSocket
from fastapi.concurrency import run_until_first_complete
from fastapi.routing import APIRouter

from explorebaduk.broadcast import broadcast
from explorebaduk.crud import get_players_by_ids, get_user_by_token, is_friend
from explorebaduk.messages import Message, PlayersAddMessage, PlayersRemoveMessage

router = APIRouter()


class Connection:
    users_online = set()

    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.user = None

    async def __aiter__(self):
        while True:
            yield self._recv()

    async def _recv(self) -> Message:
        return Message.from_string(await self.websocket.receive_text())

    async def initialize(self):
        await self.websocket.accept()
        message = await self._recv()
        if message.event == "authorize":
            if user := get_user_by_token(message.data.get("token")):
                if user.user_id not in self.users_online:
                    self.user = user
                    self.users_online.add(user.user_id)
                    await broadcast.publish("main", PlayersAddMessage(user).json())
        await self.handle_refresh()

    async def finalize(self):
        if self.user:
            self.users_online.remove(self.user.user_id)
            await broadcast.publish("main", PlayersRemoveMessage(self.user).json())

    async def handle_refresh(self):
        data = [PlayersAddMessage(player) for player in get_players_by_ids(self.users_online)]
        tasks = []
        for message in data:
            if self.user:
                message.data["friend"] = is_friend(self.user, message.data["user_id"])
            else:
                message.data["friend"] = False
            tasks.append(self.websocket.send_json(message.json()))

        await asyncio.gather(*tasks)


@router.websocket_route("/ws")
async def ws_handler(websocket: WebSocket):
    connection = Connection(websocket)
    await connection.initialize()
    await run_until_first_complete(
        (ws_receiver, {"connection": connection}),
        (ws_sender, {"connection": connection}),
    )
    await connection.finalize()


async def ws_receiver(connection: Connection):
    async for message in connection.websocket.iter_text():
        await broadcast.publish(channel="main", message=message)


async def ws_sender(connection: Connection):
    async with broadcast.subscribe(channel="main") as subscriber:
        async for event in subscriber:
            message = Message(event.message)
            if message.event == "players.add":
                if connection.user:
                    message.data["friend"] = is_friend(connection.user, message.data["user_id"])
                else:
                    message.data["friend"] = False
            await connection.websocket.send_json(message.json())
