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

        self.challenge = self._get_challenge()

    def _get_challenge(self):
        if user := self.get_user_by_token(self.request):
            for challenge in self.app.challenges:
                if user.user_id == challenge.user_id:
                    return challenge
            return Challenge(user)

    async def handle_request(self):
        await self.connect_ws()
        try:
            await self._refresh_list()
            await self.handle_message()
        finally:
            await self.disconnect_ws()

    async def connect_ws(self):
        self.connected.add(self.ws)

    async def disconnect_ws(self):
        self.connected.remove(self.ws)

    async def handle_message(self):
        while message := await self.receive_message():

            if message["action"] == "refresh":
                await self._refresh_list()

    async def _refresh_list(self):
        await asyncio.gather(
            *[
                self.send_message(challenge.as_dict())
                for challenge in self.app.challenges
                if challenge.is_active()
            ]
        )
