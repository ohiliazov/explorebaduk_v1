from sanic import response
from sanic.views import HTTPMethodView
from sanic.request import Request


class PlayerView(HTTPMethodView):
    """View to get player card"""
    async def get(self, request: Request, player_id: str):
        user = request.app.db.select_user(int(player_id))
        return response.json(user.as_dict())
