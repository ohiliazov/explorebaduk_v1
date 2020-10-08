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

        self.user = self.get_user_by_token(request)
        self.challenge = self._get_challenge()

    @property
    def excluded(self) -> set:
        return self.challenge.ws_list

    def _get_challenge(self):
        if self.user:
            for challenge in self.app.challenges:
                if self.user.user_id == challenge.user_id:
                    return challenge
            return Challenge(self.user)
        return Challenge()

    def _get_challenge_by_id(self, challenge_id: int):
        for challenge in self.app.challenges:
            if challenge_id == challenge.user_id:
                return challenge

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
        self.app.challenges.add(self.challenge)
        await self.send_message({"status": "login", "user": self.challenge.user_data})

    async def disconnect_ws(self):
        self.connected.remove(self.ws)

        async with self.challenge.lock:
            self.challenge.remove_ws(self.ws)

            if not self.challenge.ws_list:
                await self._inactivate_challenge()
                self.app.challenges.discard(self.challenge)

    async def handle_message(self):
        while message := await self.receive_message():
            if message["action"] == "refresh":
                await self._refresh_list()
            if message["action"] == "set":
                await self._set_challenge(message["challenge"])
            if message["action"] == "unset":
                await self._unset_challenge()
            if message["action"] == "join":
                await self._join_challenge(message["challenge_id"])

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
        async with self.challenge.lock:
            if not (errors := self.challenge.set(data)):
                await self.broadcast_message(
                    {
                        "status": "active",
                        "user_id": self.challenge.user_id,
                        "challenge": self.challenge.as_dict(),
                    },
                )

            await self.send_message(
                {
                    "action": "set",
                    "data": self.challenge.as_dict(),
                    "errors": errors,
                },
            )

    async def _inactivate_challenge(self):
        if self.challenge.unset():
            await self.broadcast_message(
                {
                    "status": "inactive",
                    "user_id": self.challenge.user_id,
                    "challenge": self.challenge.as_dict(),
                },
            )

    async def _unset_challenge(self):
        async with self.challenge.lock:
            await self._inactivate_challenge()
            await self.send_message(
                {
                    "action": "unset",
                    "data": self.challenge.as_dict(),
                },
            )

    async def _join_challenge(self, challenge_id: int):
        if not self.user:
            return await self.send_message({"action": "join", "status": "error", "message": "Not authorized"})

        if not (challenge := self._get_challenge_by_id(challenge_id)):
            return await self.send_message({"action": "join", "status": "error", "message": "Not found"})

        if challenge.user_id == self.user.user_id:
            return await self.send_message({"action": "join", "status": "error", "message": "Cannot join yourself"})

        async with challenge.lock:
            if not challenge.is_active():
                return await self.send_message({"action": "join", "status": "error", "message": "Not active"})

            if challenge.join(self.ws, self.user):
                await self.send_messages(challenge.ws_list, {"action": "joined", "user_id": self.user.user_id})
            await self.send_message({"action": "join", "status": "OK"})
