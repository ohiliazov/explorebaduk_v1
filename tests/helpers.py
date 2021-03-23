import asyncio
import random
from typing import List, Optional

from async_asgi_testclient import TestClient
from async_asgi_testclient.websocket import WebSocketSession

from explorebaduk.messages import AuthorizeMessage, RefreshMessage
from explorebaduk.models import UserModel


class ApiTester(TestClient):
    def authorize(self, user: UserModel):
        for token in user.tokens:
            if token.is_active():
                self.headers["Authorization"] = f"Bearer {token.token}"

    async def get_players(self, q: str = None):
        if q:
            return await self.get("/api/players", query_string={"q": q})
        return await self.get("/api/players")

    async def get_player(self, player_id: int):
        return await self.get(f"/api/players/{player_id}")

    async def get_friends(self):
        return await self.get("/api/friends")

    async def create_open_game(self, post_body: dict):
        return await self.post("/api/open-games", json=post_body)

    async def cancel_open_game(self):
        return await self.delete("/api/open-games")

    async def request_open_game(self, opponent_id: int, post_body: dict):
        return await self.post(f"/api/open-games/{opponent_id}", json=post_body)

    async def accept_open_game(self, opponent_id: int):
        return await self.post(f"/api/open-games/{opponent_id}/accept")

    async def reject_open_game(self, opponent_id: int):
        return await self.delete(f"/api/open-games/{opponent_id}/accept")

    async def create_game_invite(self, opponent_id: int, post_body: dict):
        return await self.post(f"/api/game-invites/{opponent_id}", json=post_body)

    async def remove_game_invite(self, opponent_id: int):
        return await self.delete(f"/api/game-invites/{opponent_id}")

    async def accept_game_invite(self, opponent_id: int):
        return await self.post(f"/api/game-invites/{opponent_id}/accept")

    async def reject_game_invite(self, opponent_id: int):
        return await self.delete(f"/api/game-invites/{opponent_id}/accept")


class WebSocketTester:
    def __init__(self, websocket: WebSocketSession):
        self.websocket = websocket
        self.user: Optional[UserModel] = None

    async def send(self, data: dict):
        await self.websocket.send_json(data)
        print(">", str(data))

    async def receive(self) -> List[dict]:
        messages = []

        while True:
            try:
                message = await asyncio.wait_for(self.websocket.receive_json(), 1)
                print("<", str(message))
                messages.append(message)
            except asyncio.TimeoutError:
                return messages

    async def authorize_with_token(self, token: str):
        await self.send(AuthorizeMessage(token).json())

    async def authorize_as_user(self, user: UserModel):
        for token in user.tokens:
            if token.is_active():
                self.user = user
                return await self.authorize_with_token(token.token)

    async def authorize_as_guest(self):
        await self.send({"event": "authorize", "data": None})

    async def refresh(self):
        await self.send(RefreshMessage().json())


def get_online_users(
    websockets: List[WebSocketTester],
    exclude: List[UserModel] = None,
) -> List[UserModel]:
    exclude = exclude or []
    return [websocket.user for websocket in websockets if websocket.user and websocket.user not in exclude]


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
        [websocket.receive() for websocket in websockets if websocket not in exclude_websockets],
    )
    return [t.result() for t in messages]
