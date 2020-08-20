from sanic import response
from sanic.views import HTTPMethodView
from sanic.request import Request


class PlayerView(HTTPMethodView):
    async def get(self, request: Request, player_id: str):
        if user := request.app.db.select_user(int(player_id)):
            return response.json(user.as_dict())

        return response.json({"message": "User not found"}, 404)
