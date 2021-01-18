import asyncio

from explorebaduk.resources import Feed, Observer


class ChallengesFeed(Feed):
    observer_class = Observer
    feed_name = "challenges"

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

    async def authorize(self, data):
        if self.conn.authorized:
            return await self.conn.send("error", {"message": "Already authorized"})

        await self.conn.authorize(data.get("token"))

    async def refresh(self):
        await asyncio.gather(
            *[
                self.conn.send("challenges.add", {"user_id": user_id, **challenge.data})
                for user_id, challenge in self.challenges.items()
                if challenge
            ]
        )
