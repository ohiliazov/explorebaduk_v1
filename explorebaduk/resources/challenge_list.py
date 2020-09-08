import asyncio
from typing import Dict

from explorebaduk.models import Challenge
from explorebaduk.resources.websocket_view import WebSocketView


class ChallengeAction:
    SET = "set"
    UNSET = "unset"
    JOIN = "join"
    LEAVE = "leave"


class ChallengeFeedView(WebSocketView):
    @property
    def user(self):
        return self.request.ctx.player

    @property
    def players(self):
        return self.app.players.values()

    @property
    def challenges(self) -> Dict[int, Challenge]:
        return self.app.challenges

    @property
    def challenge(self) -> Challenge:
        return self.challenges.get(self.user.user_id)

    @property
    def connected(self) -> set:
        return {challenge.ws for challenge in self.challenges.values()}

    async def handle_request(self):
        if not self.user or self.user not in self.players:
            return await self.send_message({"error": "Not logged in"})

        await self.set_online()
        try:
            await self._send_challenges_list()
            await self.handle_message()
        finally:
            await self.set_offline()

    async def set_online(self):
        self.challenges[self.user.user_id] = Challenge(self.ws, self.user)

    async def set_offline(self):
        await self._unset_challenge(self.user.user_id)
        self.challenges.pop(self.user.user_id)

        for challenge in self.challenges.values():
            await self._leave_challenge(challenge.user_id)

    async def handle_message(self):
        while message := await self.receive_message():

            if message["action"] == "refresh":
                await self._send_challenges_list()

            elif message["action"] == ChallengeAction.SET:
                await self._set_challenge(message["challenge"])

            elif message["action"] == ChallengeAction.UNSET:
                await self._unset_challenge(self.challenge.user_id)

            elif message["action"] == ChallengeAction.JOIN:
                await self._join_challenge(message["challenge_id"])

            elif message["action"] == ChallengeAction.LEAVE:
                await self._join_challenge(message["challenge_id"])

    async def _send_challenges_list(self):
        await asyncio.gather(*[
            self.send_message(challenge.as_dict())
            for challenge in self.challenges.values()
            if challenge.is_active()
        ])

    async def _set_challenge(self, data: dict):
        if self.challenge.set(data):
            await self.broadcast_message({"status": "set", "challenge": self.challenge.as_dict()})
        else:
            await self.send_message({"error": "Cannot create challenge"})

    async def _unset_challenge(self, challenge_id: int):
        if self.challenge.unset():
            await self.broadcast_message({"status": "unset", "challenge_id": challenge_id})

    async def _join_challenge(self, challenge_id: int):
        if not (challenge := self.challenges.get(challenge_id)):
            return await self.send_message({"message": "Challenge not found"})

        if not challenge.is_active() and challenge_id != self.user.user_id:
            return await self.send_message({"message": "Challenge is not active"})

        challenge.join(self.user.user_id, self.ws)
        await self.send_message({"status": "joined", "user_id": self.user.user_id}, challenge.ws)
        await self.send_message({"status": "joined", "challenge_id": challenge_id})

    async def _leave_challenge(self, challenge_id: int):
        if not (challenge := self.challenges.get(challenge_id)):
            return await self.send_message({"message": "Challenge not found"})

        if not challenge.leave(self.user.user_id):
            return

        if challenge.is_active():
            await self.send_message({"status": "left", "user": self.user.as_dict()}, challenge.ws)

        else:
            await self._unset_challenge(challenge_id)
