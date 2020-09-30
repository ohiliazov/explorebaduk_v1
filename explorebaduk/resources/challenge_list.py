import asyncio

from explorebaduk.models import Challenge
from explorebaduk.resources.websocket_view import WebSocketView
from explorebaduk.mixins import DatabaseMixin, PlayersMixin


class ChallengeFeedView(WebSocketView, PlayersMixin, DatabaseMixin):
    # not authorized -> cannot create challenge
    # not online -> cannot create challenge
    # not in players feed -> cannot create challenge
    # create - broadcast
    # remove - broadcast
    # update - broadcast
    # player offline -> remove

    connected = set()

    def __init__(self, request, ws):
        super().__init__(request, ws)

        player = self.get_player_by_token(request)
        self.challenge = Challenge(self.get_player_by_model(player))

    async def handle_request(self):

        await self.set_online()
        try:
            await self._send_challenges_list()
            await self.handle_message()
        finally:
            await self.set_offline()

    async def set_online(self):
        self.connected.add(self.ws)

    async def set_offline(self):
        self.connected.remove(self.ws)
        self.challenge.exit_event.set()

    async def handle_message(self):
        while message := await self.receive_message():

            if message["action"] == "refresh":
                await self._send_challenges_list()

    async def _send_challenges_list(self):
        await asyncio.gather(
            *[self.send_message(challenge.as_dict()) for challenge in self.app.challenges if challenge.is_active()]
        )
