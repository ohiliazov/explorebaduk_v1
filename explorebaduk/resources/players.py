import asyncio
from sanic import response
from sanic.views import HTTPMethodView

from explorebaduk.mixins import Subscriber
from explorebaduk.helpers import get_user_by_token

from .feed import BaseFeed


class RefreshPlayersView(HTTPMethodView):
    @staticmethod
    def _get_players(request):
        return request.app.players

    def _get_connection(self, request, user_id):
        for conn in self._get_players(request):
            if conn.user_id == user_id:
                return conn

    async def post(self, request):
        user = get_user_by_token(request)
        conn = self._get_connection(request, user.user_id)

        if conn is None:
            return response.json({"message": "Not connected to websocket feed"})

        await conn.send_json({"action": "refresh"})
        await asyncio.gather(
            *[
                conn.send_json({"status": "online", "player": player.user_dict()})
                for player in self._get_players(request)
                if player.authorized
            ]
        )

        return response.json({"message": "Player list refreshed"})


class PlayersFeedView(BaseFeed):
    conn_class = Subscriber

    @property
    def connected(self):
        return self.app.players

    async def run(self):
        await self._send_player_list()
        while message := await self.receive_message():
            if message["action"] == "refresh":
                await self._send_player_list()

    async def connect(self):
        async with self.conn.lock:
            self.conn.subscribe(self.ws)
            self.app.players.add(self.conn)

            if self.conn.authorized:
                await self._send_login_info()

                if len(self.conn.ws_list) == 1:
                    await self._broadcast_online()

    async def disconnect(self):
        async with self.conn.lock:
            self.conn.unsubscribe(self.ws)
            if not self.conn.ws_list:
                self.app.players.remove(self.conn)

                if self.conn.authorized:
                    await self._broadcast_offline()

    async def _send_login_info(self):
        await self.send_message({"status": "login", "user": self.conn.user_dict()})

    async def _broadcast_online(self):
        await self.broadcast_message({"status": "online", "player": self.conn.user_dict()})

    async def _broadcast_offline(self):
        await self.broadcast_message({"status": "offline", "player": self.conn.user_dict()})

    async def _send_player_list(self):
        await asyncio.gather(
            *[
                self.send_message({"status": "online", "player": player.user_dict()})
                for player in self.app.players
                if player.authorized
            ]
        )
