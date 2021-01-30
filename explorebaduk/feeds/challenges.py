import asyncio

from explorebaduk.messages import ChallengesAddMessage
from explorebaduk.resources import Connection, Feed


class ChallengesFeed(Feed):
    observer_class = Connection
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

    async def refresh(self):

        await asyncio.gather(
            *[
                self.conn.send_message(ChallengesAddMessage(user_id, challenge.data))
                for user_id, challenge in self.challenges.items()
                if challenge
            ]
        )
