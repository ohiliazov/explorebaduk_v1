import asyncio
from collections import defaultdict

from cerberus import Validator
from explorebaduk.feeds import GlobalFeed
from explorebaduk.database import UserModel
from explorebaduk.validation import challenge_schema
from explorebaduk.mixins import Subscriber


class Challenge(Subscriber):
    def __init__(self, user: UserModel = None):
        super().__init__(user)
        self.opponent = None

        self.lock = asyncio.Lock()
        self.data = None
        self.joined = defaultdict(set)
        self.connected = set()
        self.connections = set()

    def is_active(self):
        return bool(self.data)

    def set(self, data: dict):
        v = Validator(challenge_schema)
        self.data = v.validated(data)

        return v.errors

    def unset(self):
        data = self.data
        self.data = None
        return data

    def join(self, ws, user_id: int):
        self.joined[user_id].add(ws)
        return len(self.joined[user_id]) == 1

    def leave(self, user_id):
        return self.joined.pop(user_id)

    def accept(self, user_id):
        if user_id in self.joined:
            self.opponent = self.joined[user_id]
        return self.opponent


class ChallengeFeedView(GlobalFeed):
    connected = set()
    conn_class = Challenge

    @property
    def connections(self):
        return self.app.players

    @property
    def excluded(self) -> set:
        return self.conn.ws_list

    def _get_challenge_by_id(self, challenge_id: int):
        for challenge in self.app.challenges:
            if challenge_id == challenge.user_id:
                return challenge

    async def handle_request(self):
        await self._refresh_list()
        await self._handle_message()

    async def connect_ws(self):
        self.conn.subscribe(self.ws)
        self.app.challenges.add(self.conn)
        await self.send_message({"status": "login", "user": self.conn.as_dict()})

    async def disconnect_ws(self):
        async with self.conn.lock:
            self.conn.unsubscribe(self.ws)

            if not self.conn.ws_list:
                await self._inactivate_challenge()
                self.app.challenges.discard(self.conn)

    async def _handle_message(self):
        while message := await self.receive_message():
            if message["action"] == "refresh":
                await self._refresh_list()
            if message["action"] == "set":
                await self._set_challenge(message["challenge"])
            if message["action"] == "unset":
                await self._unset_challenge()
            if message["action"] == "join":
                await self._join_challenge(message["challenge_id"])
            if message["action"] == "leave":
                await self._leave_challenge(message["challenge_id"])
            if message["action"] == "accept":
                await self._accept_request(message["opponent_id"])

    async def _refresh_list(self):
        await asyncio.gather(
            *[
                self.send_message(
                    {"status": "active", "challenge": challenge.data},
                )
                for challenge in self.app.challenges
                if challenge.is_active()
            ]
        )

    async def _set_challenge(self, data: dict):
        async with self.conn.lock:
            if not (errors := self.conn.set(data)):
                await self.broadcast_message(
                    {
                        "status": "active",
                        "user_id": self.conn.user_id,
                        "challenge": self.conn.data,
                    },
                )

            await self.send_message(
                {
                    "action": "set",
                    "data": self.conn.data,
                    "errors": errors,
                },
            )

    async def _inactivate_challenge(self):
        if self.conn.unset():
            await self.broadcast_message(
                {
                    "status": "inactive",
                    "user_id": self.conn.user_id,
                    "challenge": self.conn.data,
                },
            )

    async def _unset_challenge(self):
        async with self.conn.lock:
            await self._inactivate_challenge()
            await self.send_message(
                {
                    "action": "unset",
                    "data": self.conn.data,
                },
            )

    async def _join_challenge(self, challenge_id: int):
        if not (challenge := self._get_challenge_by_id(challenge_id)):
            return await self.send_message({"action": "join", "status": "error", "message": "Not found"})

        async with challenge.lock:
            if not self.user:
                return await self.send_message({"action": "join", "status": "error", "message": "Not authorized"})

            if challenge.user_id == self.user.user_id:
                return await self.send_message({"action": "join", "status": "error", "message": "Owner cannot join"})

            if not challenge.is_active():
                return await self.send_message({"action": "join", "status": "error", "message": "Not active"})

            if challenge.join(self.ws, self.user.user_id):
                await challenge.send_json({"action": "joined", "user_id": self.user.user_id})

        await self.send_message({"action": "join", "status": "OK"})

    async def _leave_challenge(self, challenge_id: int):
        if not (challenge := self._get_challenge_by_id(challenge_id)):
            return await self.send_message({"action": "leave", "status": "error", "message": "Not found"})

        async with challenge.lock:
            if not self.user:
                return await self.send_message({"action": "leave", "status": "error", "message": "Not authorized"})

            if challenge.user_id == self.user.user_id:
                return await self.send_message({"action": "leave", "status": "error", "message": "Owner cannot leave"})

            if not challenge.is_active():
                return await self.send_message({"action": "leave", "status": "error", "message": "Not active"})

            if challenge.leave(self.user.user_id):
                await challenge.send_json({"action": "left", "user_id": self.user.user_id})
                await self.send_message({"action": "leave", "status": "OK"})

    async def _accept_request(self, opponent_id: int):
        async with self.conn.lock:
            if not self.user:
                return await self.send_message({"action": "accept", "status": "error", "message": "Not authorized"})

            if not self.conn.is_active():
                return await self.send_message({"action": "accept", "status": "error", "message": "Not active"})

            if self.conn.opponent:
                return await self.send_message({"action": "accept", "status": "error", "message": "Already accepted"})

            if opponent_ws := self.conn.accept(opponent_id):
                await self.send_messages(opponent_ws, {"action": "accepted", "user_id": self.user.user_id})
                await self.send_message({"action": "accept", "status": "OK"})
            else:
                await self.send_message({"action": "accept", "status": "error", "message": "Not joined"})
