import logging
import websockets

from constants import USER_LOGIN, USER_LOGOUT
from database import TokenModel, UserModel
from schema import LoginSchema
from handlers import BaseHandler, InvalidActionError

logger = logging.getLogger("user_handler")


class UserHandler(BaseHandler):
    PRIORITY = 5

    def __init__(self, session, sync_queue):
        super().__init__(session, sync_queue)
        self.users_online = {}

    async def handle_login(self, ws, data: dict):
        # Check if user is already logged in
        if ws in self.users_online:
            message = {
                "action": "login",
                "status": "success",
                "data": f"Logged in as {self.users_online[ws].full_name}",
            }

            return self.send(ws, message)

        # Authenticate user
        signin_data = LoginSchema().load(data)
        signin_token = self.session.query(TokenModel).filter_by(**signin_data).first()

        if not signin_token:
            message = {
                "action": "login",
                "status": "failure",
                "data": f"Authorization failed",
            }
            return self.send(ws, message)

        # Set user online
        user = self.session.query(UserModel).filter_by(user_id=signin_token.user_id).first()
        self.users_online[ws] = user
        message = {
            "action": "login",
            "status": "success",
            "data": f"Logged in as {user.full_name}"
        }
        self.send(ws, message)

        # Sync all
        sync_message = {
            "action": "sync",
            "data": {"user_online": user.user_id},
        }
        self.sync(sync_message)

    def set_offline(self, ws):
        user = self.users_online.pop(ws)
        sync_message = {
            "action": "sync",
            "data": {"user_offline": user.user_id},
        }
        self.sync(sync_message)

    async def handle_logout(self, ws: websockets.WebSocketServerProtocol):
        # Sync if user was online before
        if ws in self.users_online:
            self.set_offline(ws)

        # Return message anyway
        message = {
            "action": "login",
            "status": "success",
            "data": f"Logged out",
        }
        self.send(ws, message)

    async def handle_action(self, ws, action: str, data: dict):
        if action == USER_LOGIN:
            await self.handle_login(ws, data)

        elif action == USER_LOGOUT:
            await self.handle_logout(ws)

        else:
            raise InvalidActionError(f"Invalid action: {action}")
