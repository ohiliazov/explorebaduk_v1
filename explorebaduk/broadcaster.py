import asyncio
from typing import Awaitable, Coroutine, Set

from broadcaster import Broadcast
from sanic.request import Request
from websockets import WebSocketCommonProtocol

from explorebaduk.messages import MessageBase
from explorebaduk.resources import Connection

broadcast = Broadcast("memory://explorebaduk")


class ConnectionManager:
    def __init__(self, channel: str):
        self.channel = channel
        self.active_connections: Set[Connection] = set()

    def connect(self, connection: Connection):
        self.active_connections.add(connection)

    def disconnect(self, connection: Connection):
        self.active_connections.remove(connection)

    async def run(self, request: Request, websocket: WebSocketCommonProtocol):
        connection = Connection(request, websocket)
        await run_until_first_complete(
            self._receiver(connection),
            self._sender(connection),
        )

    async def _receiver(self, connection: Connection):
        async for message in connection:
            await broadcast.publish(channel=self.channel, message=message)

    async def _sender(self, connection: Connection):
        async with broadcast.subscribe(channel=self.channel) as subscriber:
            async for event in subscriber:
                await connection.send_message(event.message)

    async def event_handler(self, connection: Connection, message: dict):
        event = message["event"]
        try:
            getattr(self, f"handle_{event}")(connection, message["data"])
        except AttributeError:
            pass

    async def broadcast(self, message: MessageBase):
        for connection in self.active_connections:
            await connection.send_message(message)


async def run_until_first_complete(*coroutines: Awaitable[Coroutine]) -> None:
    tasks = [asyncio.create_task(coroutine) for coroutine in coroutines]
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    for task in pending:
        task.cancel()
