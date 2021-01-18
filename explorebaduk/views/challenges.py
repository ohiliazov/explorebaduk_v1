import asyncio

from sanic import response
from sanic.views import HTTPMethodView

from explorebaduk.constants import EventName
from explorebaduk.helpers import authorized
from explorebaduk.validation import create_game_schema, validate_payload


class ChallengesView(HTTPMethodView):
    @authorized()
    async def post(self, request):
        user_id = request.ctx.user.user_id
        if (challenge := request.app.challenges.get(user_id)) is None:
            return response.json({"message": "Not connected to challenge feed"}, 404)

        if challenge:
            await self.delete(request)

        data, errors = validate_payload(request.json, create_game_schema)
        if errors:
            return response.json({"message": "Game setup is not valid", "errors": errors}, 400)

        challenge.set(data)

        message_to_challenge_feed = {"message": "Challenge set"}
        message_to_challenges_feed = {"user_id": user_id, **data}
        await asyncio.gather(
            *[conn.send("set.ok", message_to_challenge_feed) for conn in request.app.feeds[f"challenges__{user_id}"]],
            *[
                conn.send(EventName.CHALLENGES_ADD, message_to_challenges_feed)
                for conn in request.app.feeds["challenges"]
            ],
        )

        return response.json({"user_id": user_id, **data}, status=201)

    @authorized()
    async def delete(self, request):
        user_id = request.ctx.user.user_id
        if (challenge := request.app.challenges.get(user_id)) is None:
            return response.json({"message": "Not connected to challenge feed"}, 404)

        if not challenge:
            return response.json({"message": "Challenge not set"}, 404)

        challenge.unset()

        message_to_challenge_feed = {"message": "Challenge unset"}
        message_to_challenges_feed = {"user_id": user_id}
        await asyncio.gather(
            *[conn.send("unset.ok", message_to_challenge_feed) for conn in request.app.feeds[f"challenges__{user_id}"]],
            *[
                conn.send(EventName.CHALLENGES_REMOVE, message_to_challenges_feed)
                for conn in request.app.feeds["challenges"]
            ],
        )

        return response.json({"message": "Challenge unset"}, status=200)
