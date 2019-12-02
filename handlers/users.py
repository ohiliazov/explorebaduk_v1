import json
import logging

from constants import UserAction
from database import SignInToken, User
from schema import LoginPayload

logger = logging.getLogger("eb_auth")


class Users:
    def __init__(self, session):
        self.session = session
        self.users = {}

    @property
    def online(self):
        return [user.email for user in self.users.values()]

    async def set_online(self, ws, user):
        self.users[ws] = user
        message = {
            "target": "user",
            "action": "login",
            "status": "success",
            "data": f"Logged in as {user.email}"
        }
        await ws.send(json.dumps(message))

    async def set_offline(self, ws):
        user = self.users.pop(ws)
        message = {
            "target": "user",
            "action": "logout",
            "status": "success",
            "data": "Logged out"
        }

        await ws.send(json.dumps(message))

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
        signin_data = LoginPayload().load(data)
        signin_token = self.session.query(SignInToken).filter_by(**signin_data).first()

        if not signin_token:
            message["status"] = "failure"
            message["data"] = "Authentication failed"
            return await ws.send(json.dumps(message))

        # Store user
        user = self.session.query(User).filter_by(user_id=signin_token.user_id).first()
        await self.set_online(ws, user)

        sync_message = {
            "target": "sync",
            "action": "user_online",
            "data": user.email
        }
        return sync_message

    async def handle_logout(self, ws, data):
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
            "data": user.email,
        }
        return sync_message

    async def handle(self, ws, action: str, data: dict) -> dict:
        if action == UserAction.LOGIN.value:
            return await self.handle_login(ws, data)

        elif action == UserAction.LOGOUT.value:
            return await self.handle_logout(ws, data)
