from typing import Optional

from fastapi import Header

from .crud import get_user_by_token
from .models import UserModel


async def get_user_from_header(authorization: str = Header(...)) -> Optional[UserModel]:
    return get_user_by_token(authorization)
