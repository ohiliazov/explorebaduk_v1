from typing import List

from sanic import response
from sanic.views import HTTPMethodView
from sanic.request import Request

from explorebaduk.models import Challenge
from explorebaduk.resources.websocket_view import WebSocketView


class ChallengeView(HTTPMethodView):
    async def get(self, request: Request, challenge_id: str):
        for challenge in request.app.challenges.values():
            if challenge.user_id == challenge_id:
                return response.json(challenge.as_dict())

        return response.json({"message": "Challenge not found"}, 404)


class ChallengeRoomView(WebSocketView):
    @property
    def connected(self) -> set:
        return set(self.challenge.joined.values())

    @property
    def user(self):
        return self.request.ctx.user

    @property
    def players(self):
        return self.app.players.values()

    @property
    def challenges(self):
        return self.app.challenges

    @property
    def active_challenges(self) -> List[Challenge]:
        return [challenge for challenge in self.challenges.values() if challenge.is_active()]

    def __init__(self, request, ws, challenge_id):
        super(ChallengeRoomView, self).__init__(request, ws)
        self.challenge_id = challenge_id
        self.challenge = None

    async def handle_request(self):
        try:
            await self.join_challenge()
        finally:
            await self.leave_challenge()

    async def join_challenge(self):
        if not self.user:
            raise Exception("Not logged in")

        for challenge in self.active_challenges:
            if challenge.user_id == self.challenge_id:
                self.challenge = challenge

        if not self.challenge and self.challenge_id != self.user.user_id:
            raise Exception("Not found")

        self.challenge.join(self.user.user_id, self.ws)
        await self.send_message({"status": "joined", "user": self.user.as_dict()}, self.challenge.user_ws)

    async def leave_challenge(self):
        pass
