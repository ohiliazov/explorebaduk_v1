import asyncio

from .feed import BaseFeed


class PlayersFeedView(BaseFeed):
    @property
    def connected(self):
        return self.app.players

    async def run(self):
        try:
            await self._connect()
            await self._refresh()
            await self._handle()
        finally:
            await self._disconnect()

    async def _connect(self):
        self.connected.add(self.conn)

    async def _handle(self):
        while True:
            try:
                event, data = await self.conn.receive()
            except Exception:
                continue

            if event == "authorize":
                await self._authorize(data)
            if event == "refresh":
                await self._refresh()

    async def _disconnect(self):
        self.connected.remove(self.conn)

        if self.conn.authorized:
            for conn in self.connected:
                if conn.user_id == self.conn.user_id:
                    break
            else:
                await self._broadcast_offline()

    async def _authorize(self, data):
        if self.conn.authorized:
            await self.conn.send("error", {"message": "WebSocket is already authorized"})

        if self.conn.authorize(data.get("token")):
            await self._send_login_info()
            for conn in self.connected:
                if conn.user_id == self.conn.user_id and conn is not self.conn:
                    break
            else:
                await self._broadcast_online()

    async def _send_login_info(self):
        await self.conn.send("players.whoami", self.conn.user.as_dict())

    async def _broadcast_online(self):
        tasks = []
        data = {
            "status": "online",
            **self.conn.user.as_dict(),
        }
        for conn in self.connected:
            conn_friend_ids = conn.user.get_friend_ids() if conn.user else []
            data["friend"] = self.conn.user_id in conn_friend_ids
            tasks.append(conn.send("players.add", data))

        await asyncio.gather(*tasks)

    async def _broadcast_offline(self):
        await self.broadcast_event("players.remove", {"user_id": self.conn.user_id})

    async def _refresh(self):
        friend_ids = self.conn.user.get_friend_ids() if self.conn.authorized else []
        await asyncio.gather(
            *[
                self.send_event(
                    "players.add",
                    {
                        "friend": player.user_id in friend_ids,
                        "status": "online",
                        **player.user.as_dict(),
                    },
                )
                for player in self.app.players
                if player.authorized
            ]
        )
