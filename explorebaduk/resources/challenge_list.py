import asyncio

from explorebaduk.models import Challenge
from explorebaduk.resources.websocket_view import WebSocketView
from explorebaduk.validation import challenge_validator


class ChallengeListView(WebSocketView):
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
