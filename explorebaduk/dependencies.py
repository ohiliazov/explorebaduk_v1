import os
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from jose import jwt

from .crud import DatabaseHandler
from .managers import UsersManager
from .models import UserModel

http_bearer = HTTPBearer()
SECRET_KEY = os.getenv("SECRET_KEY", "my-super-secret-token")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")


def get_db_session() -> DatabaseHandler:
    db = DatabaseHandler()
    try:
        yield db
    finally:
        db.session.close()


def create_access_token(user: UserModel, expires: bool = True):
    data = {"sub": user.username}

    if expires:
        data["exp"] = datetime.utcnow() + timedelta(minutes=30)

    token = jwt.encode(data, SECRET_KEY, jwt.ALGORITHMS.HS256)

    return token


def get_current_user(token: str, db: DatabaseHandler):
    try:
        payload = jwt.decode(token, SECRET_KEY, [jwt.ALGORITHMS.HS256])
        username: str = payload.get("sub")
    except jwt.JWTError:
        return None

    return db.get_user_by_username(username)


def current_user(
    token: str = Depends(oauth2_scheme),
    db: DatabaseHandler = Depends(get_db_session),
):
    if user := get_current_user(token, db):
        return user

    raise HTTPException(status.HTTP_401_UNAUTHORIZED)


async def current_user_online(user: UserModel = Depends(current_user)) -> UserModel:
    if UsersManager.is_online(user):
        return user

    raise HTTPException(400, "Not connected to websocket")
