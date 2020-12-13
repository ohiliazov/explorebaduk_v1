import asyncio

from .view import Feed, Observer


class PlayerObserver(Observer):
    def get_friends_list(self) -> set:
        return self.user.get_friends_list() if self.authorized else set()


class PlayersFeed(Feed):
    observer_class = PlayerObserver

    @property
    def observers(self):
        return self.app.players

    async def handle(self):
        await self._refresh()

        while True:
            event, data = await self.conn.receive()

            if event == "authorize":
                await self._authorize(data)
            if event == "refresh":
                await self._refresh()

    async def disconnect(self):
        if self.conn.authorized:
            for conn in self.observers:
                if conn.user_id == self.conn.user_id:
                    break
            else:
                await self._broadcast_offline()

    async def _authorize(self, data):
        if self.conn.authorized:
            await self._broadcast_offline()

        if self.conn.authorize(data.get("token")):
            await self._send_login_info()
            for conn in self.observers:
                if conn.user_id == self.conn.user_id and conn is not self.conn:
                    break
            else:
                await self._broadcast_online()

    async def _send_login_info(self):
        await self.conn.send("players.whoami", self.conn.user.as_dict())

    async def _broadcast_online(self):
        friends_list = self.conn.get_friends_list()

        await asyncio.gather(
            *[
                conn.send(
                    "players.add",
                    {
                        "status": "online",
                        "friend": conn.user_id in friends_list,
                        **self.conn.user.as_dict(),
                    },
                )
                for conn in self.observers
            ]
        )

    async def _broadcast_offline(self):
        await self.broadcast("players.remove", {"user_id": self.conn.user_id})

    async def _refresh(self):
        friends_list = self.conn.get_friends_list()
        await asyncio.gather(
            *[
                self.conn.send(
                    "players.add",
                    {
                        "status": "online",
                        "friend": player.user_id in friends_list,
                        **player.user.as_dict(),
                    },
                )
                for player in self.app.players
                if player.authorized
            ]
        )
