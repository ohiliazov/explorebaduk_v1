import asyncio

from explorebaduk.models import Challenge
from explorebaduk.resources.websocket_view import WebSocketView
from explorebaduk.mixins import DatabaseMixin
from explorebaduk.resources.explorebaduk import ExploreBadukPlayers, ExploreBadukChallenges


class ChallengeAction:
    SET = "set"
    UNSET = "unset"
    JOIN = "join"
    LEAVE = "leave"


class ChallengeFeedView(WebSocketView, ExploreBadukPlayers, ExploreBadukChallenges, DatabaseMixin):
    connected = set()

    def __init__(self, request, ws):
        super().__init__(request, ws)
        self.player = self.get_player_by_token(request)

    @property
    def challenge(self) -> Challenge:
        return self.challenges.get(self.player.user_id)

    async def handle_request(self):

        await self.set_online()
        try:
            await self._send_challenges_list()
            await self.handle_message()
        finally:
            await self.set_offline()

    async def set_online(self):
        self.challenges[self.player.user_id] = Challenge(self.ws, self.player)

    async def set_offline(self):
        await self._unset_challenge(self.player.user_id)
        challenge = self.challenges.pop(self.player.user_id)

        await challenge.exit_event.set()

    async def handle_message(self):
        while message := await self.receive_message():

            if message["action"] == "refresh":
                await self._send_challenges_list()

            elif message["action"] == ChallengeAction.SET:
                await self._set_challenge(message["challenge"])

            elif message["action"] == ChallengeAction.UNSET:
                await self._unset_challenge(self.challenge.user_id)

    async def _send_challenges_list(self):
        await asyncio.gather(
            *[
                self.send_message(challenge.as_dict())
                for challenge in self.challenges.values()
                if challenge.is_active()
            ]
        )

    async def _set_challenge(self, data: dict):
        if self.challenge.set(data):
            await self.broadcast_message({"status": "set", "challenge": self.challenge.as_dict()})
        else:
            await self.send_message({"error": "Cannot create challenge"})

    async def _unset_challenge(self, challenge_id: int):
        if self.challenge.unset():
            await self.broadcast_message({"status": "unset", "challenge_id": challenge_id})
