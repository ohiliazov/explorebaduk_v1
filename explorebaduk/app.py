import os
from collections import defaultdict

from sanic import Sanic
from sqlalchemy import create_engine

DEFAULT_DATABASE_URI = "sqlite:///explorebaduk.sqlite3"


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
    app.config["DATABASE_URI"] = os.getenv("DATABASE_URI", DEFAULT_DATABASE_URI)


def register_routes(app: Sanic):
    from explorebaduk.feeds import ChallengeOwnerFeed, ChallengesFeed, PlayersFeed
    from explorebaduk.views import ChallengesView

    app.add_websocket_route(
        PlayersFeed.as_view(),
        uri="/players",
        name="Players Feed",
    )

    app.add_websocket_route(
        ChallengesFeed.as_view(),
        uri="/challenges",
        name="Challenges Feed",
    )

    app.add_websocket_route(
        ChallengeOwnerFeed.as_view(),
        uri="/challenge/<challenge_id:int>",
        name="Challenge Owner Feed",
    )

    app.add_route(
        ChallengesView.as_view(),
        uri="/challenges",
        name="Challenges View",
    )


def register_listeners(app: Sanic):
    @app.listener("before_server_start")
    async def setup_db(app, loop):
        app.db_engine = create_engine(app.config["DATABASE_URI"])
