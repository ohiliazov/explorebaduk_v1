import random
import string
import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import create_session
from explorebaduk.models import BaseModel, UserModel, TokenModel


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


def make_token(num: int, user_id: int, minutes: int = 10):
    token_data = {
        "token_id": num,
        "user_id": user_id,
        "token": f"{string.ascii_letters}{user_id:012d}",
        "expired_at": datetime.datetime.utcnow() + datetime.timedelta(minutes=minutes),
    }
    return TokenModel(**token_data)


def populate_database_with_data(session, num_users: int):
    for i in range(num_users):
        user = make_user(i)
        token = make_token(i, i, random.randint(0, 3600))

        session.add_all([user, token])

    session.flush()


def create_db(database_uri):
    engine = create_engine(database_uri)
    session = create_session(engine)
    BaseModel.metadata.drop_all(engine)
    BaseModel.metadata.create_all(engine)
    populate_database_with_data(session, 1000)


if __name__ == "__main__":
    # database_uri = input("Enter database uri: ")
    create_db("sqlite:///explorebaduk.sqlite3")
