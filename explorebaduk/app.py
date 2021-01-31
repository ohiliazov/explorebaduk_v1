from collections import defaultdict

from sanic import Sanic

from explorebaduk.constants import APP_NAME, RouteName


class ExploreBadukApp(Sanic):
    def __init__(self, name):
        super().__init__(name=name)

        self.feeds = defaultdict(set)
        self.challenges = {}
        self.games = {}


def create_app(name: str = APP_NAME) -> Sanic:
    app = ExploreBadukApp(name)

    register_routes(app)

    return app


def register_routes(app: Sanic):
    from explorebaduk.feeds import ChallengeFeed, ChallengesFeed, PlayersFeed
    from explorebaduk.views import PlayerListView

    app.add_route(
        PlayerListView.as_view(),
        uri="/players",
        name=RouteName.PLAYERS_VIEW,
    )

    app.add_websocket_route(
        PlayersFeed.as_view(),
        uri="/ws/players",
        name=RouteName.PLAYERS_FEED,
    )

    app.add_websocket_route(
        ChallengesFeed.as_view(),
        uri="/ws/challenges",
        name=RouteName.CHALLENGES_FEED,
    )

    app.add_websocket_route(
        ChallengeFeed.as_view(),
        uri="/ws/challenges/<challenge_id:int>",
        name=RouteName.CHALLENGE_FEED,
    )


def register_listeners(app: Sanic):
    from explorebaduk.broadcaster import broadcast

    @app.listener("before_server_start")
    async def broadcast_connect(app, loop):
        broadcast.connect()

    @app.listener("after_server_stop")
    async def broadcast_disconnect(app, loop):
        broadcast.disconnect()
