import os

from sanic import Sanic
from sqlalchemy import create_engine

from explorebaduk.feeds import GamesFeed, PlayersFeed
from explorebaduk.views import GamesView, RatingView

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
        GamesFeed.as_view(),
        uri="/games",
        name="Games Feed",
    )

    app.add_route(
        GamesView.as_view(),
        uri="/games",
        name="Rating View",
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
        app.players = set()
        app.games = set()
