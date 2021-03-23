import datetime
import itertools
import random
import string
from typing import List

from explorebaduk.models import BlacklistModel, FriendshipModel, TokenModel, UserModel


def generate_token(user_id: int, expire_time: datetime.datetime) -> TokenModel:
    return TokenModel(
        user_id=user_id,
        token="".join(
            random.choices(
                string.ascii_letters + string.digits + string.punctuation,
                k=64,
            ),
        ),
        expire=expire_time,
    )


def generate_user(num: int) -> UserModel:
    # Abcdefg1
    return UserModel(
        username=f"johndoe{num}",
        first_name=f"John#{num}",
        last_name=f"Doe#{num}",
        password="$2y$10$N5ohEZckAk/9Exus/Py/5OM7pZgr8Gk6scZpH95FjvOSRWo00tVoC",
        email=f"johndoe{num}@explorebaduk.com",
        rating=random.randint(100, 3000),
        puzzle_rating=random.randint(100, 3000),
    )


def generate_friend(user_id: int, friend_id: int, *, muted=False) -> FriendshipModel:
    return FriendshipModel(
        user_id=user_id,
        friend_id=friend_id,
        muted=muted,
    )


def generate_blocked_user(user_id: int, blocked_user_id: int) -> BlacklistModel:
    return BlacklistModel(
        user_id=user_id,
        blocked_user_id=blocked_user_id,
    )


def generate_users(session, number_of_users: int) -> List[UserModel]:
    users = [generate_user(i) for i in range(number_of_users)]
    session.add_all(users)
    session.flush()
    return users


def generate_tokens(session, users: list, *, expires: bool = True, **expire_kwargs) -> List[TokenModel]:
    if expires:
        expire_time = datetime.datetime.utcnow() + datetime.timedelta(**expire_kwargs)
    else:
        expire_time = None

    tokens = [generate_token(user.user_id, expire_time) for user in users]
    session.add_all(tokens)
    session.flush()

    return tokens


def generate_friends(
    session,
    users: list,
    number_of_friends: int = 20,
    exclude_pairs: list = None,
) -> List[FriendshipModel]:
    all_pairs = list(itertools.combinations(users, 2))
    if exclude_pairs:
        all_pairs = [pair for pair in all_pairs if pair not in exclude_pairs]

    pairs = random.sample(all_pairs, number_of_friends)
    pairs += [(friend, user) for user, friend in pairs]

    friends = [
        generate_friend(
            user.user_id,
            friend.user_id,
            muted=random.choice([True, False]),
        )
        for user, friend in pairs
    ]

    session.add_all(friends)
    session.flush()

    return friends


def generate_blocked_users(
    session,
    users: list,
    number_of_blocked_users: int = 20,
    friends: List[FriendshipModel] = None,
) -> List[BlacklistModel]:
    all_pairs = list(itertools.combinations(users, 2))
    if friends:
        all_friend_pairs = [(friend.user_id, friend.friend_id) for friend in friends]
        all_pairs = [pair for pair in all_pairs if pair not in all_friend_pairs]

    pairs = random.sample(all_pairs, number_of_blocked_users)

    blocked_users = [generate_blocked_user(user.user_id, blocked_user.user_id) for user, blocked_user in pairs]

    session.add_all(blocked_users)
    session.flush()

    return blocked_users
