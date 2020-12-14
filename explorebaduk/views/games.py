import asyncio

from sanic import response
from sanic.views import HTTPMethodView

from explorebaduk.helpers import authorized, scoped_session
from explorebaduk.models import GameModel
from explorebaduk.validation import create_game_validator


def create_game(request):
    with scoped_session(request) as session:
        game = GameModel(settings=create_game_validator.normalized(request.json))
        session.add(game)
        session.flush()
        return game.as_dict()


class GamesView(HTTPMethodView):
    @authorized()
    async def post(self, request):

        if not create_game_validator.validate(request.json):
            return response.json({"message": "Game setup is not valid", "errors": create_game_validator.errors}, 400)

        game = create_game(request)
        request.app.challenges[request.ctx.user.user_id] = game

        message = {"user_id": request.ctx.user.user_id, "game": game}
        await asyncio.gather(*[conn.send("games.add", message) for conn in request.app.feeds["games"]])

        return response.json(game, status=201)
