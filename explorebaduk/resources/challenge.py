import uuid


import asyncio

from explorebaduk.resources.feed import WebSocketFeed

from sanic import response
from sanic.views import HTTPMethodView
from sanic.request import Request

from explorebaduk.helpers import validate_json
from explorebaduk.validation import challenge_create_schema


class ChallengeStatus:
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"


def challenge_created(challenge: dict) -> dict:
    return {"status": ChallengeStatus.CREATED, **challenge}


def challenge_updated(challenge: dict) -> dict:
    return {"status": ChallengeStatus.UPDATED, **challenge}


def challenge_deleted(challenge: dict) -> dict:
    return {"status": ChallengeStatus.DELETED, **challenge}


class ChallengeView(HTTPMethodView):
    @staticmethod
    async def put_message(request, message):
        await request.app.challenge_queue.put(message)

    async def get(self, request: Request, challenge_id: dict):
        if challenge := request.app.challenges.get(challenge_id):
            return response.json(challenge)

        return response.json({"message": "Challenge not found"}, 404)

    @validate_json(challenge_create_schema, clean=True)
    async def post(self, request: Request, valid_json: dict):
        if not (user := request.ctx.user):
            return response.json({"message": "Forbidden to create challenge"}, 403)

        challenge_id = str(uuid.uuid4())
        challenge = {
            **valid_json,
            "challenge_id": challenge_id,
            "user_id": user.user_id,
        }
        request.app.challenges[challenge_id] = challenge
        await self.put_message(request, challenge_created(challenge))

        return response.json({"challenge_id": challenge_id, "message": "Challenge created"})

    @validate_json(challenge_create_schema, clean=True)
    async def put(self, request: Request, challenge_id: str, valid_json: dict):
        if not (challenge := request.app.challenges.get(challenge_id)):
            return response.json({"message": "Challenge not found"}, 404)

        if not (user := request.ctx.user) or user.user_id != challenge["user_id"]:
            return response.json({"message": "Forbidden to update challenge"}, 403)

        challenge.update(valid_json)
        await self.put_message(request, challenge_updated(challenge))

        return response.json({"challenge_id": challenge_id, "message": "Challenge updated"})

    async def delete(self, request: Request, challenge_id: str):
        if not request.ctx.user:
            return response.json({"message": "Not authorized"}, 403)

        if challenge := request.app.challenges.pop(challenge_id, None):
            await self.put_message(request, challenge_deleted(challenge))
            return response.json({"challenge_id": challenge_id, "message": "Challenge deleted"})

        return response.json({"message": "Challenge not found"}, 404)


class ChallengeFeed(WebSocketFeed):
    connected = set()

    @property
    def challenges(self):
        return self.app.challenges

    @property
    def queue(self):
        return self.app.challenge_queue

    async def run(self):
        await asyncio.gather(
            self.handle_queue(),
            self.handle_refresh(),
        )

    async def handle_queue(self):
        while True:
            message = await self.queue.get()
            await self.broadcast_message(message)

    async def handle_refresh(self):
        while True:
            await self._send_challenge_list()
            await self.receive_message()

    async def _send_challenge_list(self):
        await asyncio.gather(*[self.send_message(challenge) for challenge in self.challenges.values()])
