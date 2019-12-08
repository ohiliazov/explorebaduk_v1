import asyncio
import json
import logging

import websockets

from database import create_session
from actions import USER_ACTIONS
from handlers.users import UserHandler


class GameServer:
    def __init__(self, host, port, database_uri=None):
        self.host = host
        self.port = port
        self.ws_server = None
        self.sync_queue = asyncio.PriorityQueue()
        self.session = create_session(database_uri) if database_uri else None
        self.logger = logging.getLogger('explorebaduk')

        self.user_handler = UserHandler(self.session, self.sync_queue)
        self.chats = None

    @property
    def clients(self):
        if self.ws_server:
            return self.ws_server.websockets

    async def sync_worker(self):
        while True:
            _, (receiver, sync_data) = await self.sync_queue.get()
            message = json.dumps(sync_data)
            if receiver:
                await receiver.send(message)

            elif self.clients:
                await asyncio.wait([ws.send(message) for ws in self.clients])

            self.logger.debug("OUT >> %s", message)
            self.sync_queue.task_done()

    async def consume_message(self, ws: websockets.WebSocketServerProtocol, message: str):
        try:
            json_data = json.loads(message)
            action = json_data.get('action')
            data = json_data.get('data')

            if action in USER_ACTIONS:
                await self.user_handler.handle_action(ws, action, data)
            else:
                self.logger.info("SKIP %s", message)

        except json.decoder.JSONDecodeError as err:
            errmsg = '%s: line %d column %d (char %d)' % (err.msg, err.lineno, err.colno, err.pos)
            message = {"status": "failure", "errors": errmsg}
            return await ws.send(json.dumps(message))

    async def register(self, ws):
        message = {
            "action": "sync",
            "data": {
                "users": [user.full_name for user in self.user_handler.users_online.values()],
                "games": [],
                "challenges": [],
            }
        }
        self.sync_queue.put_nowait((3, (ws, message)))

    async def unregister(self, ws):
        if ws in self.user_handler.users_online:
            self.user_handler.set_offline(ws)

    async def run(self, ws: websockets.WebSocketServerProtocol, path: str):
        await self.register(ws)
        try:
            async for message in ws:
                self.logger.debug("IN <<< %s", message)
                await self.consume_message(ws, message)
        except websockets.WebSocketException:
            pass
        finally:
            await self.unregister(ws)

    def serve(self):
        server = websockets.serve(self.run, self.host, self.port)
        self.ws_server = server.ws_server
        asyncio.get_event_loop().run_until_complete(server)
        asyncio.get_event_loop().run_until_complete(self.sync_worker())
        asyncio.get_event_loop().run_forever()
