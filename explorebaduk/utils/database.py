import random
import datetime

from explorebaduk.database import UserModel, TokenModel


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
        'token': f'token_{user_id}',
        'expired_at': datetime.datetime.utcnow() + datetime.timedelta(minutes=minutes),
    }
    return TokenModel(**token_data)


def populate_database_with_data(db, num_users: int):
    for i in range(num_users):
        user = make_user(i)
        token = make_token(i, random.randint(0, 3600))

        db.add(user)
        db.add(token)

    db.commit()
    db.close()
