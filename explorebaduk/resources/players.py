import asyncio

from explorebaduk.feeds import GlobalFeed
from explorebaduk.database import UserModel
from explorebaduk.mixins import Subscriber


class Player(Subscriber):
    def __init__(self, user: UserModel = None):
        super().__init__(user)

        self.lock = asyncio.Lock()


class PlayersFeedView(GlobalFeed):
    connected = set()
    conn_class = Player

    @property
    def connections(self):
        return self.app.players

    @property
    def excluded(self) -> set:
        return self.conn.ws_list

    async def handle_request(self):
        await self._send_player_list()
        await self.handle_message()

    async def connect_ws(self):
        async with self.conn.lock:
            self.conn.subscribe(self.ws)
            self.app.players.add(self.conn)

            if self.conn.authorized:
                await self._send_login_info()

                if len(self.conn.ws_list) == 1:
                    await self._broadcast_online()

    async def disconnect_ws(self):
        async with self.conn.lock:
            self.conn.unsubscribe(self.ws)
            if not self.conn.ws_list:
                self.app.players.remove(self.conn)

                if self.conn.authorized:
                    await self._broadcast_offline()

    async def handle_message(self):
        while message := await self.receive_message():
            if message["action"] == "refresh":
                await self._send_player_list()

    async def _send_login_info(self):
        await self.send_message({"status": "login", "user": self.conn.as_dict()})

    async def _broadcast_online(self):
        await self.broadcast_message({"status": "online", "player": self.conn.as_dict()})

    async def _broadcast_offline(self):
        await self.broadcast_message({"status": "offline", "player": self.conn.as_dict()})

    async def _send_player_list(self):
        await asyncio.gather(
            *[
                self.send_message({"status": "online", "player": player.as_dict()})
                for player in self.app.players
                if player.authorized
            ]
        )
