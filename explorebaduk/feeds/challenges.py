from explorebaduk.resources import Feed, Observer


class ChallengesFeed(Feed):
    observer_class = Observer

    @property
    def observers(self):
        return self.app.feeds["challenges"]

    async def handle(self):
        await self.ws.wait_closed()

    async def disconnect(self):
        pass
