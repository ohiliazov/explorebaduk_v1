import asyncio
import json

import websockets
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from handlers import handle_message

Session = sessionmaker()


class GameServer:
    clients = {}

    def __init__(self, host, port, database_uri):
        self.host = host
        self.port = port
        self.db_engine = create_engine(database_uri)
        self.session = Session(bind=self.db_engine)

    @classmethod
    async def register(cls, ws: websockets.WebSocketServerProtocol) -> None:
        host, port = ws.remote_address[:2]
        print(f'Connected: {host} {port}')
        cls.clients[ws] = None

    @classmethod
    async def unregister(cls, ws: websockets.WebSocketServerProtocol) -> None:
        host, port = ws.remote_address[:2]
        print(f'Disconnected: {host} {port}')
        cls.clients.pop(ws)

    async def run(self, ws: websockets.WebSocketServerProtocol, path: str):
        await self.register(ws)
        try:
            async for message in ws:
                data = json.loads(message)
                await handle_message(self.session, ws, data)
        except websockets.WebSocketException:
            pass
        finally:
            await self.unregister(ws)

    def serve(self):
        eb_server = websockets.serve(self.run, self.host, self.port)

        asyncio.get_event_loop().run_until_complete(eb_server)
        asyncio.get_event_loop().run_forever()
