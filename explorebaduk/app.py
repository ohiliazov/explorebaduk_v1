from sanic import Sanic
from sanic.request import Request
from explorebaduk.database import DatabaseHandler
from explorebaduk.resources.v1 import PlayerCardView, players_feed_handler


def create_app() -> Sanic:
    app = Sanic("ExploreBaduk Game Server API")
    app.config.from_envvar("CONFIG_PATH")
    register_listeners(app)
    register_routes(app)
    register_middleware(app)
    return app


def register_routes(app: Sanic):
    app.add_route(
        PlayerCardView.as_view(),
        "/players/<player_id>",
        methods=["GET"],
        name="Player Info"
    )

    app.add_websocket_route(
        players_feed_handler,
        "/players",
        name="Players Feed"
    )


def register_listeners(app: Sanic):

    @app.listener('before_server_start')
    async def setup_db(app, loop):
        app.db = DatabaseHandler(app.config["DATABASE_URI"])

    @app.listener('before_server_start')
    async def setup_data(app, loop):
        app.players = {}
        app.challenges = NotImplemented
        app.games = NotImplemented


def register_middleware(app: Sanic):

    @app.middleware("request")
    def authorize_user(request: Request):
        auth_token = request.headers.get("Authorization")
        request.ctx.user = app.db.get_user_by_token(auth_token)
