from sanic import response
from sanic.views import HTTPMethodView
from sanic.request import Request


class PlayerView(HTTPMethodView):
    async def get(self, request: Request, player_id: str):
        if player := request.app.db.select_player(int(player_id)):
            return response.json(player.as_dict())

        return response.json({"message": "User not found"}, 404)
