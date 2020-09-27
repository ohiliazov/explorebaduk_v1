from sanic import response
from sanic.views import HTTPMethodView
from sanic.request import Request

from explorebaduk.mixins import DatabaseMixin


class PlayerView(HTTPMethodView, DatabaseMixin):
    async def get(self, request: Request, player_id: str):
        if player := self.get_player_by_id(request, int(player_id)):
            return response.json(player.as_dict())

        return response.json({"message": "User not found"}, 404)
