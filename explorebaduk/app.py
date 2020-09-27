import os

from sanic import Sanic
from sanic.request import Request
from explorebaduk.database import DatabaseHandler
from explorebaduk.resources import (
    PlayerView,
    PlayersFeedView,
    ChallengeView,
    ChallengeFeedView,
)


def create_app() -> Sanic:
    app = Sanic("ExploreBaduk Game Server API")

    register_config(app)
    register_listeners(app)
    register_routes(app)
    register_middleware(app)

    return app


def register_config(app):
    if "CONFIG_PATH" in os.environ:
        app.config.from_envvar("CONFIG_PATH")

    if "DATABASE_API" in os.environ:
        app.config["DATABASE_API"] = os.getenv("DATABASE_API")


def register_routes(app: Sanic):

    app.add_websocket_route(PlayersFeedView.as_view(), "/players", name="Players Feed")
    app.add_websocket_route(ChallengeFeedView.as_view(), "/challenges", name="Challenges Feed")
    app.add_route(PlayerView.as_view(), "/players/<player_id>", methods=["GET"], name="Player Info")
    app.add_route(ChallengeView.as_view(), "/challenge/<challenge_id>", methods=["GET"], name="Challenge Info")


def register_listeners(app: Sanic):
    @app.listener("before_server_start")
    async def setup_db(app, loop):
        app.db = DatabaseHandler(app.config["DATABASE_URI"])

    @app.listener("before_server_start")
    async def setup_data(app, loop):
        app.connected = {}
        app.players = {}
        app.challenges = {}


def register_middleware(app: Sanic):
    @app.middleware("request")
    def authorize_user(request: Request):
        auth_token = request.headers.get("Authorization")
        request.ctx.player = app.db.get_user_by_token(auth_token)
