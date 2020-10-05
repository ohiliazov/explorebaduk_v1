import asyncio

from explorebaduk.models import Challenge
from explorebaduk.resources.websocket_view import WebSocketView
from explorebaduk.mixins import DatabaseMixin


class ChallengeFeedView(WebSocketView, DatabaseMixin):
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
        self._task = None

    def _get_challenge(self):
        if user := self.get_user_by_token(self.request):
            for challenge in self.app.challenges:
                if user.user_id == challenge.user_id:
                    return challenge
            return Challenge(user)
        return Challenge()

    async def handle_request(self):
        await self.connect_ws()
        try:
            await self._refresh_list()
            await self.handle_message()
        finally:
            await self.disconnect_ws()

    async def connect_ws(self):
        self.connected.add(self.ws)
        self.challenge.add_ws(self.ws)
        await self.send_message({"status": "login", "user": self.challenge.user_data})

    async def disconnect_ws(self):
        self.connected.remove(self.ws)
        self.challenge.remove_ws(self.ws)

    async def handle_message(self):
        while message := await self.receive_message():
            if message["action"] == "refresh":
                await self._refresh_list()
            if message["action"] == "set":
                await self._set_challenge(message["challenge"])
            if message["action"] == "unset":
                await self._unset_challenge()

    async def _refresh_list(self):
        await asyncio.gather(
            *[
                self.send_message(
                    {"status": "active", "challenge": challenge.as_dict()},
                )
                for challenge in self.app.challenges
                if challenge.is_active()
            ]
        )

    async def _set_challenge(self, data: dict):
        self.challenge.set(data)
        await self.broadcast_message(
            {
                "status": "active",
                "user_id": self.challenge.user_id,
                "challenge": self.challenge.as_dict(),
            },
            exclude_ws=self.challenge.ws_list,
        )
        if self._task is not None:
            self._task.cancel()
        self._task = asyncio.create_task(self._unset_when_offline())

    async def _unset_when_offline(self):
        await self.challenge.wait_offline()
        await self._unset_challenge()

    async def _unset_challenge(self):
        self.challenge.unset()
        await self.broadcast_message(
            {
                "status": "inactive",
                "user_id": self.challenge.user_id,
                "challenge": self.challenge.as_dict(),
            },
            exclude_ws=self.challenge.ws_list,
        )
        if self._task is not None:
            self._task.cancel()
