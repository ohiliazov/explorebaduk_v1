import asyncio

from explorebaduk.resources import Feed, Observer


class ChallengesFeed(Feed):
    observer_class = Observer

    @property
    def observers(self):
        return self.app.feeds["challenges"]

    @property
    def challenges(self) -> dict:
        return self.app.challenges

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
                await self._remove_challenge()

    async def _remove_challenge(self):
        try:
            self.challenges.pop(self.conn.user_id)
        except KeyError:
            await self.conn.send("error", {"message": "Challenge not created"})
        else:
            await self.broadcast("challenge.remove", {"user_id": self.conn.user_id})

    async def _authorize(self, data):
        if self.conn.authorized:
            await self.conn.send("error", {"message": "Already authorized"})

        elif self.conn.authorize(data.get("token")):
            await self._send_login_info()

    async def _send_login_info(self):
        await self.conn.send("challenges.whoami", self.conn.user.as_dict())

    async def _refresh(self):
        await asyncio.gather(
            *[
                self.conn.send("challenges.add", {"user_id": user_id, **challenge})
                for user_id, challenge in self.challenges.items()
            ]
        )
