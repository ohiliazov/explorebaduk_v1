from typing import Iterable, List, Tuple

from sqlalchemy import and_, or_

from .database import scoped_session
from .models import FriendshipModel, GameModel, GamePlayerModel, TokenModel, UserModel
from .schemas import Color, GameCategory, GameType, RuleSet


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


def get_friendships(user_id: int) -> List[Tuple[int, int]]:
    with scoped_session() as session:
        return (
            session.query(
                FriendshipModel.user_id,
                FriendshipModel.friend_id,
            )
            .filter(
                or_(
                    FriendshipModel.user_id == user_id,
                    FriendshipModel.friend_id == user_id,
                ),
            )
            .all()
        )


def create_game(
    name: str,
    rules: RuleSet,
    game_type: GameType,
    category: GameCategory,
    board_size: int,
    handicap: int,
    komi: float,
    time_settings: dict,
):
    game = GameModel(
        name=name,
        rules=rules,
        game_type=game_type,
        category=category,
        board_size=board_size,
        handicap=handicap,
        komi=komi,
        time_settings=time_settings,
    )

    with scoped_session() as session:
        session.add(game)
        session.flush()
        return game.game_id


def create_game_player(game_id: int, user_id: int, color: Color, time_left: int):
    game_player = GamePlayerModel(game_id=game_id, user_id=user_id, color=color, time_left=time_left)

    with scoped_session() as session:
        session.add(game_player)
        session.flush()
