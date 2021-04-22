from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .crud import DatabaseHandler
from .models import UserModel
from .shared import UsersManager

http_bearer = HTTPBearer()


async def current_user(
    token: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> UserModel:
    with DatabaseHandler() as db:
        if user := db.get_user_by_token(token.credentials):
            return user

    raise HTTPException(401, "Unauthorized")


async def current_user_online(user: UserModel = Depends(current_user)) -> UserModel:
    if UsersManager.is_online(user):
        return user

    raise HTTPException(400, "Not connected to websocket")
