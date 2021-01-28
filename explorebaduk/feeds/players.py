import asyncio

from explorebaduk.messages import ErrorMessage, PlayersAddMessage, PlayersRemoveMessage
from explorebaduk.resources import Connection, Feed


class PlayerObserver(Connection):
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
            await self._broadcast_offline()

    async def authorize(self, data):
        if self.conn.authorized:
            return await self.conn.send_message(ErrorMessage("Already authorized"))

        if await self.conn.authorize(data.get("token"), self.get_online_user_ids()):
            await self._broadcast_online()

    async def _broadcast_online(self):
        friends_list = self.conn.get_friends_list()

        await asyncio.gather(
            *[
                conn.send_message(
                    PlayersAddMessage(
                        self.conn.user,
                        conn.user_id in friends_list,
                    ),
                )
                for conn in self.observers
            ]
        )

    async def _broadcast_offline(self):
        await self.broadcast(PlayersRemoveMessage(self.conn.user))

    async def refresh(self, *args):
        friends_list = self.conn.get_friends_list()
        await asyncio.gather(
            *[
                self.conn.send_message(
                    PlayersAddMessage(
                        conn.user,
                        conn.user_id in friends_list,
                    ),
                )
                for conn in self.observers
                if conn.authorized
            ]
        )
