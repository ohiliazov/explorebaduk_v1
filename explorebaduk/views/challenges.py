import asyncio

from sanic import response
from sanic.views import HTTPMethodView

from explorebaduk.helpers import authorized
from explorebaduk.validation import create_game_validator


class ChallengesView(HTTPMethodView):
    @authorized()
    async def post(self, request):
        if not create_game_validator.validate(request.json):
            return response.json({"message": "Game setup is not valid", "errors": create_game_validator.errors}, 400)

        if request.ctx.user.user_id in request.app.challenges:
            event_name = "challenges.update"
        else:
            event_name = "challenges.add"

        challenge = create_game_validator.normalized(request.json)
        request.app.challenges[request.ctx.user.user_id] = challenge

        message = {"user_id": request.ctx.user.user_id, **challenge}
        await asyncio.gather(*[conn.send(event_name, message) for conn in request.app.feeds["challenges"]])

        return response.json(challenge, status=201)

    @authorized()
    async def delete(self, request):
        try:
            challenge = request.app.challenges.pop(request.ctx.user.user_id)
        except KeyError:
            return response.json({"message": "Challenge not created"}, 404)

        message = {"user_id": request.ctx.user.user_id}
        await asyncio.gather(*[conn.send("challenges.remove", message) for conn in request.app.feeds["challenges"]])

        return response.json(challenge, status=200)
