import datetime
import random
import string

from sqlalchemy import create_engine
from sqlalchemy.orm import create_session

from explorebaduk.models import (
    BaseModel,
    BlockedUserModel,
    FriendModel,
    TokenModel,
    UserModel,
)


def make_user(num: int):
    user_data = {
        "user_id": num,
        "username": f"johndoe{num}",
        "first_name": "John",
        "last_name": f"Doe#{num}",
        "email": f"johndoe{num}@explorebaduk.com",
        "rating": random.randint(0, 3000),
        "puzzle_rating": random.randint(0, 3000),
    }
    return UserModel(**user_data)


def make_friend(user_id: int, friend_id: int, *, muted=False):
    user_data = {
        "user_id": user_id,
        "friend_id": friend_id,
        "muted": muted,
    }
    return FriendModel(**user_data)


def make_blocked_user(user_id: int, blocked_user_id: int):
    user_data = {
        "user_id": user_id,
        "blocked_user_id": blocked_user_id,
    }
    return BlockedUserModel(**user_data)


def make_token(num: int, user_id: int, minutes: int = 10):
    token_data = {
        "id": num,
        "user_id": user_id,
        "token": f"{string.ascii_letters}{user_id:012d}",
        "expired_at": datetime.datetime.utcnow() + datetime.timedelta(minutes=minutes),
    }
    return TokenModel(**token_data)


def populate_database_with_data(session, num_users: int, num_friends: int = 0):
    for i in range(num_users):
        user = make_user(i)
        token = make_token(i, i, random.randint(0, 3600))

        session.add_all([user, token])

    for i in range(5):
        for j in range(i + 1, 5):
            friend_i = make_friend(i, j, muted=j > 3)
            friend_j = make_friend(j, i, muted=i > 3)
            session.add_all([friend_i, friend_j])

    for i in range(5):
        for j in range(i + 6, 10):
            blocked_user = make_blocked_user(i, j)
            session.add(blocked_user)

    session.flush()


def create_db(database_uri):
    engine = create_engine(database_uri)
    session = create_session(engine)
    BaseModel.metadata.drop_all(engine)
    BaseModel.metadata.create_all(engine)
    populate_database_with_data(session, 1000)


if __name__ == "__main__":
    create_db("sqlite:///explorebaduk.sqlite3")
