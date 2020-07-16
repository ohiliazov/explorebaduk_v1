import asyncio
from sanic import Sanic
from sanic.request import Request
from explorebaduk.database import DatabaseHandler
from explorebaduk.resources.player import PlayerView, PlayersFeed
from explorebaduk.resources.challenge import ChallengeView, ChallengeFeed


def create_app() -> Sanic:
    app = Sanic("ExploreBaduk Game Server API")
    app.config.from_envvar("CONFIG_PATH")
    register_listeners(app)
    register_routes(app)
    register_middleware(app)
    return app


def register_routes(app: Sanic):
    app.add_route(PlayerView.as_view(), "/players/<player_id>", methods=["GET"], name="Player Info")
    app.add_route(ChallengeView.as_view(), "/challenges", methods=["POST"])
    app.add_route(ChallengeView.as_view(), "/challenges/<challenge_id>", methods=["GET", "POST", "DELETE"])

    app.add_websocket_route(PlayersFeed.as_feed(), "/players_feed")
    app.add_websocket_route(ChallengeFeed.as_feed(), "/challenges_feed")


def register_listeners(app: Sanic):
    @app.listener("before_server_start")
    async def setup_db(app, loop):
        app.db = DatabaseHandler(app.config["DATABASE_URI"])

    @app.listener("before_server_start")
    async def setup_data(app, loop):
        app.connected = set()
        app.players = set()
        app.challenges = {}
        app.challenge_queue = asyncio.Queue()


def register_middleware(app: Sanic):
    @app.middleware("request")
    def authorize_user(request: Request):
        auth_token = request.headers.get("Authorization")
        request.ctx.user = app.db.get_user_by_token(auth_token)
