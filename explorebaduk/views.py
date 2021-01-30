from sanic import response
from sanic.request import Request
from sanic.views import HTTPMethodView

from explorebaduk.crud import get_players_list


class PlayerListView(HTTPMethodView):
    async def get(self, request: Request):
        players = get_players_list(request.args.get("q"))

        return response.json([player.as_dict() for player in players])
