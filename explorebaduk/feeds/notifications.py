import asyncio

from explorebaduk.resources import Feed, Observer


class NotificationsFeed(Feed):
    observer_class = Observer

    @property
    def observers(self):
        return self.app.feeds["notifications"]

    @property
    def notifications(self) -> set:
        if self.conn.authorized:
            return self.app.notifications[self.conn.user_id]
        return set()

    async def handle(self):
        await self._refresh()

        while True:
            event, data = await self.conn.receive()
            if event == "authorize":
                await self._authorize(data)
            if event == "refresh":
                await self._refresh()

    async def finalize(self):
        pass

    async def _authorize(self, data):
        if self.conn.authorized:
            await self.conn.send("error", {"message": "Already authorized"})

        elif self.conn.authorize(data.get("token")):
            await self._send_login_info()

    async def _send_login_info(self):
        await self.conn.send("notifications.whoami", self.conn.user.as_dict())

    async def _refresh(self):
        await asyncio.gather(
            *[self.conn.send("notifications.add", notification) for notification in self.notifications]
        )
