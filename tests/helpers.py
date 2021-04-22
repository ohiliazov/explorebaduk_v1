import asyncio
import random
from typing import List, Optional

from async_asgi_testclient import TestClient
from async_asgi_testclient.websocket import WebSocketSession

from explorebaduk.models import UserModel


class ApiTester(TestClient):
    def authorize(self, user: UserModel):
        for token in user.tokens:
            if token.is_active():
                self.headers["Authorization"] = f"Bearer {token.token}"

    async def get_players(self, params: dict = None):
        return await self.get("/api/players", query_string=params)

    async def get_player(self, player_id: int):
        return await self.get(f"/api/players/{player_id}")

    async def get_friends(self):
        return await self.get("/api/friends")

    async def get_user_friends(self, user_id: int):
        return await self.get(f"/api/friends/{user_id}")


class WebSocketTester:
    def __init__(self, websocket: WebSocketSession):
        self.websocket = websocket
        self.user: Optional[UserModel] = None

    async def receive(self) -> List[dict]:
        messages = []

        while True:
            try:
                message = await asyncio.wait_for(self.websocket.receive_json(), 1)
                print("<", str(message))
                messages.append(message)
            except asyncio.TimeoutError:
                return messages

    async def authorize_as_user(self, user: UserModel):
        for token in user.tokens:
            if token.is_active():
                self.user = user
                return await self.websocket.send_text(token.token)

    async def authorize_as_guest(self):
        await self.websocket.send_text("")


def get_online_users(
    websockets: List[WebSocketTester],
    exclude: List[UserModel] = None,
) -> List[UserModel]:
    exclude = exclude or []
    return [
        websocket.user
        for websocket in websockets
        if websocket.user and websocket.user not in exclude
    ]


def get_offline_users(
    users: List[UserModel],
    websockets: List[WebSocketTester],
    exclude: List[UserModel] = None,
) -> List[UserModel]:
    websocket_users = get_online_users(websockets, exclude)
    return [user for user in users if user not in websocket_users]


def random_websocket(
    websockets: List[WebSocketTester],
    *,
    exclude_users: List[UserModel] = None,
    exclude_guests: bool = True,
) -> WebSocketTester:
    if exclude_guests:
        websockets = filter(lambda ws: ws.user, websockets)
    if exclude_users:
        websockets = filter(lambda ws: ws not in exclude_users, websockets)

    return random.choice(list(websockets))


async def receive_websockets(
    websockets: List[WebSocketTester], exclude_websockets: List[WebSocketTester] = None
) -> List[List[dict]]:
    exclude_websockets = exclude_websockets or []
    messages, _ = await asyncio.wait(
        [
            websocket.receive()
            for websocket in websockets
            if websocket not in exclude_websockets
        ],
    )
    return [t.result() for t in messages]
