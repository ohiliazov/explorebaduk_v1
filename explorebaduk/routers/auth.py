from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext

from ..crud import DatabaseHandler
from ..dependencies import create_access_token, current_user
from ..models import UserModel

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter(tags=["authentication"])


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    with DatabaseHandler() as db:
        user = db.get_user_by_username(form_data.username)

        if not user:
            raise HTTPException(401, "Unauthorized")

        if not verify_password(form_data.password, user.password):
            raise HTTPException(401, "Unauthorized")

        token = create_access_token(user)

    return {"access_token": token}


@router.post("/whoami")
def check_authentication(user: UserModel = Depends(current_user)):
    return user.asdict()
