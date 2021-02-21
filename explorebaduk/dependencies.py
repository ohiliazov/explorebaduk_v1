from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .crud import get_user_by_token
from .models import UserModel

http_bearer = HTTPBearer()


async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> UserModel:
    if user := get_user_by_token(token.credentials):
        return user

    raise HTTPException(401, "Unauthorized")
