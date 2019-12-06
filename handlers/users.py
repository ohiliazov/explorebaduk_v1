import asyncio
import json
import logging
import websockets

from actions import USER_LOGIN, USER_LOGOUT
from database import TokenModel, UserModel
from schema import LoginMessage

logger = logging.getLogger("eb_auth")


class Users:
    def __init__(self, session, sync_queue):
        self.session = session
        self.sync_queue = sync_queue
        self.users = {}

    @property
    def users_online(self):
        return [user.email for user in self.users.values()]

    def send_user_status(self, user: UserModel, online: bool):
        sync_message = {
            "target": "sync",
            "action": "user_online" if online else "user_offline",
            "data": {
                "user_id": user.user_id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "rating": user.rating,
            },
        }
        self.sync_queue.put_nowait(sync_message)

    async def handle_login(self, ws, data):
        message = {
            "target": "user",
            "action": "login",
        }

        # Check if user is already logged in
        if ws in self.users:
            message["status"] = "success"
            message["data"] = f"Already logged in as {self.users[ws].email}"

            return await ws.send(json.dumps(message))

        # Authenticate user
        signin_data = LoginMessage().load(data)
        signin_token = self.session.query(TokenModel).filter_by(**signin_data).first()

        if not signin_token:
            message["status"] = "failure"
            message["data"] = "Authentication failed"
            return await ws.send(json.dumps(message))

        # Add user to online list
        user = self.session.query(UserModel).filter_by(user_id=signin_token.user_id).first()
        self.users[ws] = user
        message = {
            "target": "user",
            "action": "login",
            "status": "success",
            "data": f"Logged in"
        }
        await ws.send(json.dumps(message))
        self.send_user_status(user, online=True)

    async def handle_logout(self, ws: websockets.WebSocketServerProtocol, data):
        message = {
            "target": "user",
            "action": "logout",
        }
        if ws not in self.users:
            message["status"] = "success"
            message["data"] = "User was not logged in"

            return await ws.send(json.dumps(message))

        user = self.users.pop(ws)
        message["status"] = "success"
        message["data"] = "Logged out"

        await ws.send(json.dumps(message))

        sync_message = {
            "target": "sync",
            "action": "user_offline",
            "data": {
                "user_id": user.user_id
            },
        }
        self.sync_queue.put_nowait(sync_message)

    async def handle(self, ws, action: str, data: dict):
        if action == USER_LOGIN:
            await self.handle_login(ws, data)

        elif action == USER_LOGOUT:
            await self.handle_logout(ws, data)
