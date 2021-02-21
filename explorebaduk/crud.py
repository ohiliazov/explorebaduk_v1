from typing import Iterable, List, Tuple

from sqlalchemy import and_, or_

from .database import scoped_session
from .models import FriendModel, TokenModel, UserModel


def get_player_by_id(user_id: int) -> UserModel:
    with scoped_session() as session:
        return session.query(UserModel).get(user_id)


def get_players_list(
    id_list: Iterable[int] = None,
    search_string: str = None,
) -> List[UserModel]:
    with scoped_session() as session:
        query = session.query(UserModel)

        if id_list is not None:
            query = query.filter(UserModel.user_id.in_(id_list))

        if search_string:
            if " " not in search_string:
                query = query.filter(
                    or_(
                        UserModel.first_name.contains(search_string),
                        UserModel.last_name.contains(search_string),
                        UserModel.username.contains(search_string),
                    ),
                )
            else:
                s1, s2 = search_string.split(" ")[:2]
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


def get_user_by_token(token) -> UserModel:
    with scoped_session() as session:

        auth_token = (
            session.query(TokenModel)
            .filter(
                TokenModel.token == token,
            )
            .first()
        )

        if auth_token and auth_token.is_active():
            return auth_token.user


def get_friendships(user: UserModel) -> List[Tuple[int, int]]:
    if user:
        with scoped_session() as session:
            return (
                session.query(
                    FriendModel.user_id,
                    FriendModel.friend_id,
                )
                .filter(
                    or_(
                        FriendModel.user_id == user.user_id,
                        FriendModel.friend_id == user.user_id,
                    ),
                )
                .all()
            )
    return []
