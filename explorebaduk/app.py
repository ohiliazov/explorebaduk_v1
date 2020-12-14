import os
from collections import defaultdict

from sanic import Sanic
from sqlalchemy import create_engine

from explorebaduk.feeds import ChallengesFeed, PlayersFeed
from explorebaduk.views import ChallengesView, RatingView

DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///explorebaduk.sqlite3")


def create_app() -> Sanic:
    app = Sanic("ExploreBaduk Game Server API")

    register_config(app)
    register_listeners(app)
    register_routes(app)

    return app


def register_config(app):
    app.config["DATABASE_URI"] = DATABASE_URI


def register_routes(app: Sanic):

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

    app.add_route(
        ChallengesView.as_view(),
        uri="/challenges",
        name="Challenges View",
    )

    app.add_route(
        RatingView.as_view(),
        uri="/rating",
        name="Rating View",
    )


def register_listeners(app: Sanic):
    @app.listener("before_server_start")
    async def setup_db(app, loop):
        app.db_engine = create_engine(app.config["DATABASE_URI"])

    @app.listener("before_server_start")
    async def setup_data(app, loop):
        app.feeds = defaultdict(set)
        app.challenges = {}
