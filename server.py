import asyncio
import json
import logging

from marshmallow.exceptions import ValidationError
import websockets

from database import create_session
from actions import TARGET_USER
from handlers.users import Users
from schema import WebSocketMessage


class GameServer:
    def __init__(self, host, port, database_uri=None):
        self.host = host
        self.port = port
        self.ws_server = None
        self.sync_queue = asyncio.Queue()
        self.session = create_session(database_uri) if database_uri else None
        self.logger = logging.getLogger('explorebaduk')

        self.users = Users(self.session, self.sync_queue)
        self.chats = None

    @property
    def clients(self):
        if self.ws_server:
            return self.ws_server.websockets

    async def sync_worker(self):
        while True:
            sync_message = json.dumps(await self.sync_queue.get())

            if self.clients:
                await asyncio.wait([ws.send(sync_message) for ws in self.clients])
                self.logger.info(f">>> {sync_message}")

            self.sync_queue.task_done()

    async def consume_message(self, ws: websockets.WebSocketServerProtocol, message: str):
        try:
            data = WebSocketMessage().loads(message)

            target = data.pop('target')
            action = data.pop('action')

            if target == TARGET_USER:
                await self.users.handle(ws, action, data)
            else:
                self.logger.info("SKIP %s", message)

        except json.decoder.JSONDecodeError as err:
            errmsg = '%s: line %d column %d (char %d)' % (err.msg, err.lineno, err.colno, err.pos)
            message = {"status": "failure", "errors": errmsg}
            return await ws.send(json.dumps(message))

        except ValidationError as err:
            message = {"status": "failure", "errors": err.messages}
            return await ws.send(json.dumps(message))

    async def sync_user(self, ws):
        tasks = []
        users_online = self.users.users_online
        if users_online:
            message = {
                'target': 'sync',
                'action': 'who_is_online',
                'data': json.dumps(users_online)
            }
            tasks.append(ws.send(json.dumps(message)))

        if tasks:
            await asyncio.wait(tasks)

    async def set_offline(self, ws):
        if ws in self.users.users:
            user = self.users.users.pop(ws)
            message = {"target": "sync", "action": "user_offline", "data": user.email}
            self.sync_queue.put_nowait(message)

    async def run(self, ws: websockets.WebSocketServerProtocol, path: str):
        await self.sync_user(ws)
        try:
            async for message in ws:
                self.logger.info("<<< %s", message)
                await self.consume_message(ws, message)
        except websockets.WebSocketException:
            pass
        finally:
            await self.set_offline(ws)

    def serve(self):
        server = websockets.serve(self.run, self.host, self.port)
        self.ws_server = server.ws_server
        asyncio.get_event_loop().run_until_complete(server)
        asyncio.get_event_loop().run_until_complete(self.sync_worker())
        asyncio.get_event_loop().run_forever()
