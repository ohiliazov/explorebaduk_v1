from sanic import response
from sanic.views import HTTPMethodView
from sanic.request import Request


class ChallengeView(HTTPMethodView):
    async def get(self, request: Request, challenge_id: str):
        for challenge in request.app.challenges.values():
            if challenge.user_id == challenge_id:
                return response.json(challenge.as_dict())

        return response.json({"message": "Challenge not found"}, 404)
