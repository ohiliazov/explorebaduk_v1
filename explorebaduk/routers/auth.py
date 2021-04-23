from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext

from explorebaduk.crud import DatabaseHandler
from explorebaduk.dependencies import create_access_token
from explorebaduk.schemas import User, UserCreate

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


@router.post("/signup", response_model=User)
def signup(user_data: UserCreate):
    user_data.password = get_password_hash(user_data.password)

    try:
        with DatabaseHandler() as db:
            user = db.create_user(user_data)
    except Exception:
        raise HTTPException(400, "Cannot create user")

    return user
