import asyncio

from sanic import response
from sanic.views import HTTPMethodView

from explorebaduk.helpers import authorized
from explorebaduk.validation import create_game_validator


class GamesView(HTTPMethodView):
    @authorized()
    async def post(self, request):

        if not create_game_validator.validate(request.json):
            return response.json({"message": "Game setup is not valid", "errors": create_game_validator.errors}, 400)

        data = create_game_validator.normalized(request.json)
        data["user_id"] = request.ctx.user.user_id
        await asyncio.gather(*[conn.send("games.add", data) for conn in request.app.games])
        return response.json(data, status=201)
