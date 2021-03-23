from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .crud import get_user_by_token
from .models import UserModel
from .shared import UsersOnline

http_bearer = HTTPBearer()


async def current_user(
    token: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> UserModel:
    if user := get_user_by_token(token.credentials):
        return user

    raise HTTPException(401, "Unauthorized")


async def current_user_online(user: UserModel = Depends(current_user)) -> UserModel:
    if UsersOnline.is_online(user):
        return user

    raise HTTPException(400, "Not connected to websocket")
