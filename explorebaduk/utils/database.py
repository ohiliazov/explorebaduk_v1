import random
import string
import datetime
from config import DATABASE_URI
from explorebaduk.database import BaseModel, UserModel, TokenModel, create_session


def make_user(num: int):
    user_data = {
        'user_id': num,
        'first_name': "John",
        'last_name': f"Doe#{num}",
        'email': f'johndoe{num}@explorebaduk.com',
        'rating': random.randint(0, 3000),
        'puzzle_rating': random.randint(0, 3000),
    }
    return UserModel(**user_data)


def make_token(num: int, user_id: int, minutes: int = 10):
    token_data = {
        'token_id': num,
        'user_id': user_id,
        'token': f'{string.ascii_letters}{user_id:012d}',
        'expired_at': datetime.datetime.utcnow() + datetime.timedelta(minutes=minutes),
    }
    return TokenModel(**token_data)


def populate_database_with_data(db, num_users: int):
    for i in range(num_users):
        user = make_user(i)
        token = make_token(i, i, random.randint(0, 3600))

        db.add(user)
        db.add(token)

    db.commit()
    db.close()


def create_db():
    session = create_session(DATABASE_URI)
    BaseModel.metadata.drop_all(session.bind)
    BaseModel.metadata.create_all(session.bind)
    populate_database_with_data(session, 1000)


if __name__ == '__main__':
    create_db()
