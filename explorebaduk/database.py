import os
from typing import List

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from explorebaduk.models import (
    BaseModel,
    BlacklistModel,
    ChallengeModel,
    FriendshipModel,
    GameModel,
    GamePlayerModel,
    UserModel,
)
from explorebaduk.schemas import ChallengeCreate, GameCreate, GamePlayer, UserCreate

engine = create_engine(os.getenv("DATABASE_URI"))
Session = sessionmaker(engine, autocommit=True, expire_on_commit=False)


class DatabaseHandler:
    def __init__(self, session: Session = None):
        self.session = session or Session()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def add(self, instance: BaseModel) -> BaseModel:
        self.session.add(instance)
        self.session.flush()
        return instance

    def get_user_by_id(self, user_id: int) -> UserModel:
        return self.session.query(UserModel).get(user_id)

    def get_user_by_email(self, email: str) -> UserModel:
        return self.session.query(UserModel).filter(UserModel.email == email).first()

    def create_user(self, data: UserCreate) -> UserModel:
        return self.add(
            UserModel(
                first_name=data.first_name,
                last_name=data.last_name,
                username=data.username,
                password=data.password,
                email=data.email,
                country=data.country,
                rating=data.rating,
            ),
        )

    def get_users(self, user_ids: List[int] = None) -> List[UserModel]:
        query = self.session.query(UserModel)
        if user_ids:
            query = query.filter(UserModel.user_id.in_(user_ids))

        return query.all()

    def search_users(self, search_string: str) -> List[UserModel]:
        if not search_string:
            return self.get_users()

        if " " not in search_string:
            return (
                self.session.query(UserModel)
                .filter(
                    UserModel.first_name.contains(search_string)
                    | UserModel.last_name.contains(search_string)
                    | UserModel.username.contains(search_string),
                )
                .all()
            )

        s1, s2 = search_string.split(" ", maxsplit=1)

        return (
            self.session.query(UserModel)
            .filter(
                (UserModel.first_name.contains(s1) & UserModel.last_name.contains(s2))
                | (
                    UserModel.first_name.contains(s2) & UserModel.last_name.contains(s1)
                ),
            )
            .all()
        )

    def get_friendship(self, user_id: int, friend_id: int) -> FriendshipModel:
        return (
            self.session.query(FriendshipModel)
            .filter(
                FriendshipModel.user_id == user_id,
                FriendshipModel.friend_id == friend_id,
            )
            .first()
        )

    def get_following(self, user_id: int) -> List[FriendshipModel]:
        return (
            self.session.query(FriendshipModel)
            .filter(FriendshipModel.user_id == user_id)
            .all()
        )

    def get_followers(self, user_id: int) -> List[FriendshipModel]:
        return (
            self.session.query(FriendshipModel)
            .filter(FriendshipModel.friend_id == user_id)
            .all()
        )

    def follow_user(self, user_id: int, friend_id: int) -> FriendshipModel:
        return self.add(FriendshipModel(user_id=user_id, friend_id=friend_id))

    def get_blocked_users(self, user_id: int) -> List[BlacklistModel]:
        return (
            self.session.query(BlacklistModel)
            .filter(BlacklistModel.user_id == user_id)
            .all()
        )

    def get_blocked_user(self, user_id: int, blocked_user_id: int) -> BlacklistModel:
        return (
            self.session.query(BlacklistModel)
            .filter(
                BlacklistModel.user_id == user_id,
                BlacklistModel.blocked_user_id == blocked_user_id,
            )
            .first()
        )

    def block_user(self, user_id: int, blocked_user_id: int) -> BlacklistModel:
        return self.add(
            BlacklistModel(user_id=user_id, blocked_user_id=blocked_user_id),
        )

    def get_game_by_id(self, game_id: int) -> GameModel:
        return self.session.query(GameModel).get(game_id)

    def create_game(self, data: GameCreate):
        return self.add(
            GameModel(
                name=data.name,
                private=data.private,
                ranked=data.ranked,
                board_size=data.board_size,
                rules=data.rules,
                speed=data.speed,
                initial_time=data.time_control.get_total_time(),
                time_control=data.time_control.dict(),
                handicap=data.handicap,
                komi=data.komi,
            ),
        )

    def get_challenge_by_id(self, challenge_id: int) -> ChallengeModel:
        return self.session.query(ChallengeModel).get(challenge_id)

    def get_open_challenges(self, user_id: int = None) -> List[ChallengeModel]:
        query = self.session.query(ChallengeModel)
        if user_id:
            query = query.filter(ChallengeModel.user_id == user_id)
        query = query.filter(ChallengeModel.opponent_id.is_(None))
        return query.all()

    def get_direct_challenges(self, user_id: int) -> List[ChallengeModel]:
        return (
            self.session.query(ChallengeModel)
            .filter(
                (ChallengeModel.opponent_id == user_id)
                | (ChallengeModel.creator_id == user_id)
                & ChallengeModel.opponent_id.is_not(None),
            )
            .all()
        )

    def get_challenges_from_user(self, user_id: int) -> List[ChallengeModel]:
        return (
            self.session.query(ChallengeModel)
            .filter(
                (ChallengeModel.creator_id == user_id)
                & ChallengeModel.opponent_id.is_not(None),
            )
            .all()
        )

    def get_challenges_to_user(self, user_id: int) -> List[ChallengeModel]:
        return (
            self.session.query(ChallengeModel)
            .filter(ChallengeModel.opponent_id == user_id)
            .all()
        )

    def create_challenge(
        self,
        user: UserModel,
        game: GameModel,
        data: ChallengeCreate,
    ) -> ChallengeModel:
        return self.add(
            ChallengeModel(
                game=game,
                creator=user,
                opponent_id=data.opponent_id,
                creator_color=data.creator_color,
                min_rating=data.min_rating,
                max_rating=data.max_rating,
            ),
        )

    def get_game_players(self, game_id: int) -> List[GamePlayerModel]:
        return (
            self.session.query(GamePlayerModel)
            .filter(
                GamePlayerModel.game_id == game_id,
            )
            .all()
        )

    def get_game_player(self, game_id: int, user_id: int) -> GamePlayerModel:
        return (
            self.session.query(GamePlayerModel)
            .filter(
                GamePlayerModel.game_id == game_id,
                GamePlayerModel.user_id == user_id,
            )
            .first()
        )

    def create_game_player(self, data: GamePlayer) -> GamePlayerModel:
        return self.add(
            GamePlayerModel(
                game_id=data.game_id,
                user_id=data.user_id,
                color=data.color,
                time_left=data.time_left,
            ),
        )
