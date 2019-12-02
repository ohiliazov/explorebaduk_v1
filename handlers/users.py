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

    async def handle_login(self, ws, data):
        if ws in self.users:
            message = {
                "target": "user",
                "data": f"Already logged in as {self.users[ws].email}"
            }
            return message

        signin_data = LoginPayload().load(data)
        signin_token = self.session.query(SignInToken).filter_by(**signin_data).first()

        if not signin_token:
            logger.info("Authentication failed for: %s", signin_data)
            return await ws.send(
                json.dumps({"status": "failure", "message": "Authentication failed"}))

        user = self.session.query(User).filter_by(user_id=signin_token.user_id).first()

        logger.info("User online: %s", user.email)
        await ws.send(json.dumps({"status": "success", "message": f"Logged in as {user.email}"}))

        self.users[ws] = user
        message = {
            "target": "user",
            "action": "online",
            "data": {
                "email": user.email,
            },
        }
        return message

    async def handle_logout(self, ws):
        user = self.users.pop(ws)
        message = {
            "target": "users",
            "action": "offline",
            "data": {
                "email": user.email,
            },
        }

        return message

    async def handle(self, ws, action: str, data: dict) -> str:
        if action == UserAction.LOGIN.value:
            return await self.handle_login(ws, data)

        elif action == UserAction.LOGIN.value:
            return await self.handle_login(ws, data)
