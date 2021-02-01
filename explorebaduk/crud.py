import datetime
from typing import List, Set

from sqlalchemy import and_, or_

from .database import scoped_session
from .models import FriendModel, TokenModel, UserModel


def get_players_list(q: str) -> List[UserModel]:
    with scoped_session() as session:
        query = session.query(UserModel)

        if q:
            if " " not in q:
                query = query.filter(
                    or_(
                        UserModel.first_name.contains(q),
                        UserModel.last_name.contains(q),
                        UserModel.username.contains(q),
                    ),
                )
            else:
                s1, s2 = q.split(" ")[:2]
                query = query.filter(
                    or_(
                        and_(
                            UserModel.first_name.contains(s1),
                            UserModel.last_name.contains(s2),
                        ),
                        and_(
                            UserModel.first_name.contains(s2),
                            UserModel.last_name.contains(s1),
                        ),
                    ),
                )

        return query.all()


def get_players_by_ids(id_list: Set[int]) -> List[UserModel]:
    with scoped_session() as session:
        return session.query(UserModel).filter(UserModel.user_id.in_(id_list)).all()


def get_user_by_token(token) -> UserModel:
    with scoped_session() as session:
        auth_token = (
            session.query(TokenModel)
            .filter(
                TokenModel.token == token,
                TokenModel.expire >= datetime.datetime.utcnow(),
            )
            .first()
        )

        if auth_token:
            return auth_token.user


def is_friend(user: UserModel, user_id):
    with scoped_session() as session:
        query = session.query(FriendModel).filter(FriendModel.user_id == user.user_id, FriendModel.friend_id == user_id)

        return query.count() > 0
