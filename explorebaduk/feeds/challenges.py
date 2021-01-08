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
                await self._remove_challenge()

    async def authorize(self, data):
        await self.conn.authorize(data.get("token"))

    async def _remove_challenge(self):
        try:
            self.challenges.pop(self.conn.user_id)
        except KeyError:
            await self.conn.send("error", {"message": "Challenge not created"})
        else:
            await self.broadcast("challenge.remove", {"user_id": self.conn.user_id})

    async def refresh(self):
        await asyncio.gather(
            *[
                self.conn.send("challenges.add", {"user_id": user_id, **challenge})
                for user_id, challenge in self.challenges.items()
            ]
        )
