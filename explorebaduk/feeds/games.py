from explorebaduk.resources import Feed, Observer


class GamesFeed(Feed):
    observer_class = Observer

    @property
    def observers(self):
        return self.app.games

    async def handle(self):
        await self.ws.wait_closed()

    async def disconnect(self):
        pass
