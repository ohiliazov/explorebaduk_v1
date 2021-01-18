import os
from collections import defaultdict

from sanic import Sanic
from sqlalchemy import create_engine

from explorebaduk.constants import APP_NAME, RouteName


class ExploreBadukApp(Sanic):
    def __init__(self, name):
        super().__init__(name=name)

        self.feeds = defaultdict(set)
        self.challenges = {}
        self.games = {}


def create_app(name: str = APP_NAME) -> Sanic:
    app = ExploreBadukApp(name)

    register_config(app)
    register_listeners(app)
    register_routes(app)

    return app


def register_config(app):
    app.config["DATABASE_URI"] = os.getenv("DATABASE_URI", "sqlite:///explorebaduk.sqlite3")


def register_routes(app: Sanic):
    from explorebaduk.feeds import ChallengeFeed, ChallengesFeed, PlayersFeed
    from explorebaduk.views import ChallengesView

    app.add_websocket_route(
        PlayersFeed.as_view(),
        uri="/players",
        name=RouteName.PLAYERS_FEED,
    )

    app.add_websocket_route(
        ChallengesFeed.as_view(),
        uri="/challenges",
        name=RouteName.CHALLENGES_FEED,
    )

    app.add_websocket_route(
        ChallengeFeed.as_view(),
        uri="/challenges/<challenge_id:int>",
        name=RouteName.CHALLENGE_FEED,
    )

    app.add_route(
        ChallengesView.as_view(),
        uri="/challenges",
        name=RouteName.CHALLENGES_VIEW,
    )


def register_listeners(app: Sanic):
    @app.listener("before_server_start")
    async def setup_db(app, loop):
        app.db_engine = create_engine(app.config["DATABASE_URI"])
