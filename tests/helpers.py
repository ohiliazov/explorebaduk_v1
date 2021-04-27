import asyncio
import random
from typing import List, Optional

from async_asgi_testclient import TestClient
from async_asgi_testclient.websocket import WebSocketSession

from explorebaduk.dependencies import create_access_token
from explorebaduk.models import UserModel


class ApiTester(TestClient):
    def authorize(self, user: UserModel):
        self.headers["Authorization"] = f"Bearer {create_access_token(user)}"

    async def get_players(self, params: dict = None):
        return await self.get("/api/players", query_string=params)

    async def get_player(self, player_id: int):
        return await self.get(f"/api/players/{player_id}")

    async def get_followers(self):
        return await self.get("/api/me/followers")

    async def get_following(self):
        return await self.get("/api/me/following")

    async def create_challenge(self, post_data: dict):
        return await self.post("/api/challenges", json=post_data)

    async def cancel_challenge(self, challenge_id: int):
        return await self.delete(f"/api/challenges/{challenge_id}")

    async def accept_challenge(self, challenge_id: int):
        return await self.post(f"/api/challenges/{challenge_id}/accept")


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
        await self.websocket.send_text(create_access_token(user))
        self.user = user

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
        websockets = filter(lambda ws: ws.user not in exclude_users, websockets)

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
