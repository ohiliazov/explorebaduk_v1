import asyncio

from explorebaduk.resources import Feed, Observer


class PlayerObserver(Observer):
    def get_friends_list(self) -> set:
        return self.user.get_friends_list() if self.authorized else set()


class PlayersFeed(Feed):
    observer_class = PlayerObserver
    feed_name = "players"

    @property
    def handlers(self) -> dict:
        return {
            "authorize": self.authorize,
            "refresh": self.refresh,
        }

    async def initialize(self):
        await self.refresh()

    async def finalize(self):
        if self.conn.authorized:
            for conn in self.observers:
                if conn.user_id == self.conn.user_id:
                    break
            else:
                await self._broadcast_offline()

    async def authorize(self, data):
        if self.conn.authorized:
            return await self.conn.send("error", {"message": "Already authorized"})

        if await self.conn.authorize(data.get("token")):
            for conn in self.observers:
                if conn.user_id == self.conn.user_id and conn is not self.conn:
                    break
            else:
                await self._broadcast_online()

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

    async def refresh(self, *args):
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
                for player in self.observers
                if player.authorized
            ]
        )
