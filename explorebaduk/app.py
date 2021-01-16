import os
from collections import defaultdict

from sanic import Sanic
from sqlalchemy import create_engine

from explorebaduk.constants import RouteName


class ExploreBadukApp(Sanic):
    feeds = defaultdict(set)
    challenges = {}
    games = {}


def create_app(app_name="ExploreBaduk") -> Sanic:
    app = ExploreBadukApp(app_name)

    register_config(app)
    register_listeners(app)
    register_routes(app)

    return app


def register_config(app):
    app.config["DATABASE_URI"] = os.getenv("DATABASE_URI", "sqlite:///explorebaduk.sqlite3")


def register_routes(app: Sanic):
    from explorebaduk.feeds import ChallengeFeed, ChallengeListFeed, PlayersFeed
    from explorebaduk.views import ChallengesView

    app.add_websocket_route(
        PlayersFeed.as_view(),
        uri="/players",
        name=RouteName.PLAYERS_FEED,
    )

    app.add_websocket_route(
        ChallengeListFeed.as_view(),
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
