import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from jose import jwt

from explorebaduk.database import DatabaseHandler
from explorebaduk.models import UserModel

http_bearer = HTTPBearer()
SECRET_KEY = os.getenv("SECRET_KEY", "my-super-secret-key")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")


def db_handler() -> DatabaseHandler:
    db = DatabaseHandler()
    try:
        yield db
    finally:
        db.session.close()


def create_token(user: UserModel, expires: bool = True):
    data = {"sub": user.email}

    if expires:
        data["exp"] = datetime.utcnow() + timedelta(hours=12)

    token = jwt.encode(data, SECRET_KEY, jwt.ALGORITHMS.HS256)

    return token


def parse_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, SECRET_KEY, [jwt.ALGORITHMS.HS256])
        return payload.get("sub")
    except jwt.JWTError:
        return None


def current_user(
    token: str = Depends(oauth2_scheme),
    db: DatabaseHandler = Depends(db_handler),
):
    if email := parse_token(token):
        if user := db.get_user_by_email(email):
            return user

    raise HTTPException(status.HTTP_401_UNAUTHORIZED)
