import asyncio

from explorebaduk.mixins import Subscriber

from .feed import BaseFeed


class PlayersFeedView(BaseFeed):
    conn_class = Subscriber

    @property
    def connected(self):
        return self.app.players

    async def run(self):
        try:
            await self._connect()
            await self._send_player_list()
            await self._handle()
        finally:
            await self._disconnect()

    async def _connect(self):
        async with self.conn.lock:
            self.conn.subscribe(self.ws)

            if self.conn.authorized:
                await self._send_login_info()

                if len(self.conn.ws_list) == 1:
                    await self._broadcast_online()

    async def _handle(self):
        while message := await self.ws.recv():
            if message == "refresh":
                await self._send_player_list()

    async def _disconnect(self):
        async with self.conn.lock:
            self.conn.unsubscribe(self.ws)
            if not self.conn.ws_list:
                self.app.players.remove(self.conn)

                if self.conn.authorized:
                    await self._broadcast_offline()

    async def _send_login_info(self):
        await self.send_message({"status": "login", "user": self.conn.user_dict()})

    async def _broadcast_online(self):
        await self.broadcast_message({"status": "online", "player": self.conn.user_dict()})

    async def _broadcast_offline(self):
        await self.broadcast_message({"status": "offline", "player": self.conn.user_dict()})

    async def _send_player_list(self):
        await asyncio.gather(
            *[
                self.send_message({"status": "online", "player": player.user_dict()})
                for player in self.app.players
                if player.authorized
            ]
        )
