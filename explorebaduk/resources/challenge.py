import asyncio

from explorebaduk.resources.feed import WebSocketFeed
from explorebaduk.validation import challenge_validator


class Challenge:
    def __init__(self, creator_id, challenge: dict):
        self.creator_id = creator_id
        self.challenge = challenge
        self.is_active = True
        self.joined = {}

    def join(self, user_id, ws):
        self.joined[user_id] = ws

    def leave(self, user_id):
        self.joined.pop(user_id, None)

    def select(self, user_id):
        return self.joined.get(user_id)

    @property
    def creator_ws(self):
        return self.joined[self.creator_id]


class ChallengeFeedBase(WebSocketFeed):
    pass


class ChallengeListFeed(WebSocketFeed):
    connected = set()

    @property
    def user(self):
        return self.request.ctx.user

    @property
    def challenges(self):
        return self.app.challenges

    async def run(self):
        while True:
            message = await self.receive_json()
            action = message.get("action")

            if action == "refresh":
                await self.refresh()

            elif action == "delete":
                await self.delete_challenge()

            elif challenge := self.validate_challenge(message):
                await self.create_challenge(challenge)

    async def refresh(self):
        await asyncio.gather(*[self.send_message(challenge) for challenge in self.challenges.values()])

    def validate_challenge(self, challenge: dict):
        if challenge_validator.validate(challenge):
            return challenge_validator.normalized(challenge)

    async def create_challenge(self, challenge):
        self.challenges[self.user.user_id] = Challenge(self.user.user_id, challenge)

        message = {
            "user_id": self.user.user_id,
            "challenge": challenge,
        }
        await self.broadcast_message(message)

    async def delete_challenge(self):
        if self.challenges.pop(self.user.user_id, None):
            message = {"user_id": self.user.user_id, "challenge": None}
            await self.broadcast_message(message)

    async def finalize(self):
        await super().finalize()
        await self.delete_challenge()


class ChallengeFeed(WebSocketFeed):
    connected = set()

    @property
    def user(self):
        return self.request.ctx.user

    @property
    def user_id(self):
        return self.user.user_id

    @property
    def challenges(self):
        return self.app.challenges

    @property
    def challenge(self) -> Challenge:
        return self.challenges[self.user_id]

    async def initialize(self):
        if not self.challenge:
            return

        if self.user_id == self.challenge.creator_id:
            self.challenge.is_active = True

        self.challenge.joined[self.user_id] = self.ws

    async def run(self):
        if not self.challenge:
            return await self.send_message({"message": "Challenge not found"})

        if not self.challenge.is_active:
            return await self.send_message({"message": "Challenge not active"})

    async def finalize(self):
        if not self.challenge:
            return

        if self.user_id == self.challenge.creator_id:
            await asyncio.gather(*[ws.close() for ws in self.challenge.joined.values()])
            self.challenges.pop(self.user_id)
        else:
            self.challenge.joined.pop(self.user_id)
