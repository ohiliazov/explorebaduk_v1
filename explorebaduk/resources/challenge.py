import asyncio
from typing import List

from explorebaduk.resources.feed import WebSocketFeed
from explorebaduk.validation import challenge_validator


class Challenge:
    def __init__(self, user, data: dict = None):
        self.user = user
        self.data = data
        self.joined = {}

    @property
    def user_id(self):
        return self.user.user_id

    @property
    def user_ws(self):
        return self.joined.get(self.user_id)

    def join(self, user_id, ws):
        self.joined[user_id] = ws

    def leave(self, user_id):
        self.joined.pop(user_id, None)

    def select(self, user_id):
        return self.joined.get(user_id)

    def is_active(self):
        return self.data is not None

    def set(self, data: dict):
        if challenge_validator.validate(data):
            self.data = challenge_validator.normalized(data)

        return self.data

    def unset(self):
        if data := self.data:
            self.data = None

        return data

    def as_dict(self):
        return {
            "user_id": self.user_id,
            "challenge": self.data,
        }


class ChallengeListFeed(WebSocketFeed):
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
    def active_challenges(self):
        return (challenge for challenge in self.challenges.values() if challenge.is_active())

    @property
    def connected(self) -> set:
        return set(self.challenges)

    async def handle_request(self):
        await self.set_online()
        try:
            await self._send_challenges_list()
            await self.handle_message()
        finally:
            await self.set_offline()

    async def set_online(self):
        if not self.user or self.user not in self.players:
            raise Exception("Not logged in")

        self.challenges[self.ws] = Challenge(self.ws, self.user)

    async def set_offline(self):
        if self.user.user_id in self.challenges:
            await self._unset_challenge()
            self.challenges.pop(self.ws)

    async def handle_message(self):
        while message := await self.receive_message():

            if message == "refresh":
                await self._send_challenges_list()

            elif message == "delete":
                await self._unset_challenge()

            elif isinstance(message, dict):
                await self._set_challenge(message)

    async def _send_challenges_list(self):
        await asyncio.gather(*[self.send_message(challenge.as_dict()) for challenge in self.active_challenges])

    async def _set_challenge(self, message: dict):
        challenge = self.challenges[self.ws]
        if challenge.set(message):
            await self.broadcast_message(challenge.as_dict())
        else:
            await self.send_message({"errors": challenge_validator.errors})

    async def _unset_challenge(self):
        challenge = self.challenges[self.ws]
        if challenge.unset():
            await self.broadcast_message(challenge.as_dict())


class ChallengeFeed(WebSocketFeed):
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
        super(ChallengeFeed, self).__init__(request, ws)
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
