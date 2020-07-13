from sanic import response
from sanic.views import HTTPMethodView
from sanic.request import Request


class PlayerCardView(HTTPMethodView):
    """View to get player card"""
    async def get(self, request: Request, player_id: str):
        x = request.app.db.select_user(int(player_id))
        return response.json({"player_id": player_id, "x": x})
