import os
from datetime import datetime
from typing import List, Tuple

from sqlalchemy import and_, create_engine, or_
from sqlalchemy.orm import Session

from .database import scoped_session
from .models import FriendshipModel, GameModel, GamePlayerModel, TokenModel, UserModel
from .schemas import Color, GameCategory, GameType, RuleSet

engine = create_engine(os.getenv("DATABASE_URI"))


class DatabaseHandler:
    def __enter__(self):
        self.session = Session(engine, autocommit=True, autoflush=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def get_user_by_token(self, token) -> UserModel:
        query = (
            self.session.query(
                TokenModel,
            )
            .filter(
                TokenModel.token == token,
            )
            .filter(
                or_(
                    TokenModel.expire.is_(None),
                    TokenModel.expire >= datetime.utcnow(),
                ),
            )
        )
        if auth_token := query.first():
            return auth_token.user

    def get_user_by_id(self, user_id: int) -> UserModel:
        return self.session.query(UserModel).get(user_id)

    def get_users(self, q: str = None) -> List[UserModel]:
        query = self.session.query(UserModel)

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


def create_game_player(
    game_id: int,
    user_id: int,
    color: Color,
    time_left: int,
):
    game_player = GamePlayerModel(
        game_id=game_id,
        user_id=user_id,
        color=color,
        time_left=time_left,
    )

    with scoped_session() as session:
        session.add(game_player)
        session.flush()
