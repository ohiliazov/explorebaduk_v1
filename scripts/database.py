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
        "username": f"johndoe{num}",
        "first_name": "John",
        "last_name": f"Doe#{num}",
        "password": "$2y$10$N5ohEZckAk/9Exus/Py/5OM7pZgr8Gk6scZpH95FjvOSRWo00tVoC",  # Abcdefg1
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


def make_token(user_id: int, minutes: int = 10):
    token_data = {
        "user_id": user_id,
        "token": f"{string.ascii_letters}{user_id:012d}",
        "expire": datetime.datetime.utcnow() + datetime.timedelta(minutes=minutes),
    }
    return TokenModel(**token_data)


def populate_database_with_data(session, num_users: int, num_friends: int = 0):
    users = []
    for i in range(num_users):
        user = make_user(i)
        users.append(user)
    session.add_all(users)
    session.flush()
    min_user_id = min([user.user_id for user in users])
    tokens = []
    friends = []
    blocked_users = []
    for idx, user in enumerate(users):
        token = make_token(user.user_id, random.randint(0, 3600))
        tokens.append(token)
        for friend in users[idx:5]:
            friends.append(make_friend(user.user_id, friend.user_id, muted=friend.user_id > min_user_id + 3))
            friends.append(make_friend(friend.user_id, user.user_id, muted=user.user_id > min_user_id + 3))

        for blocked_user in users[5:10]:
            blocked_users.append(make_blocked_user(user.user_id, blocked_user.user_id))

    session.add_all(tokens + friends + blocked_users)
    session.flush()


def create_db(database_uri):
    engine = create_engine(database_uri)
    session = create_session(engine)
    BaseModel.metadata.drop_all(engine)
    BaseModel.metadata.create_all(engine)
    populate_database_with_data(session, 20)


if __name__ == "__main__":
    # create_db("mysql+pymysql://root@localhost:3306/explorebaduk_new")
    create_db("sqlite:///explorebaduk.sqlite3")
