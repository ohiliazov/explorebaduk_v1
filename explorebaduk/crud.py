import os
import random
from typing import List

from sqlalchemy import and_, create_engine, or_
from sqlalchemy.orm import Session

from .models import (
    ChallengeModel,
    FriendshipModel,
    GameModel,
    GamePlayerModel,
    UserModel,
)
from .schemas import Challenge, Color, Game

engine = create_engine(os.getenv("DATABASE_URI"))


class DatabaseHandler:
    def __enter__(self):
        self.session = Session(engine, autocommit=True, expire_on_commit=False)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def get_user_by_id(self, user_id: int) -> UserModel:
        return self.session.query(UserModel).get(user_id)

    def get_user_by_username(self, username: str) -> UserModel:
        return (
            self.session.query(UserModel).filter(UserModel.username == username).first()
        )

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

        return query.order_by(UserModel.user_id).all()

    def get_following(self, user_id: int) -> List[FriendshipModel]:
        return (
            self.session.query(FriendshipModel)
            .filter(FriendshipModel.user_id == user_id)
            .order_by(FriendshipModel.friend_id)
            .all()
        )

    def get_followers(self, user_id: int) -> List[FriendshipModel]:
        return (
            self.session.query(FriendshipModel)
            .filter(FriendshipModel.friend_id == user_id)
            .order_by(FriendshipModel.user_id)
            .all()
        )

    def create_game(self, game: Game) -> GameModel:
        game = GameModel(
            name=game.name,
            private=game.private,
            ranked=game.ranked,
            board_size=game.board_size,
            rules=game.rules,
            speed=game.speed,
            initial_time=game.time_control.get_total_time(),
            time_control=game.time_control.dict(),
            handicap=game.handicap,
            komi=game.komi,
        )
        self.session.add(game)
        return game

    def get_challenge_by_id(self, challenge_id: int) -> ChallengeModel:
        return self.session.query(ChallengeModel).get(challenge_id)

    def list_challenges(self) -> List[ChallengeModel]:
        return (
            self.session.query(ChallengeModel)
            .filter(ChallengeModel.opponent_id.is_(None))
            .all()
        )

    def list_outgoing_challenges(self, user_id: int) -> List[ChallengeModel]:
        return (
            self.session.query(ChallengeModel)
            .filter(
                ChallengeModel.creator_id == user_id,
                ChallengeModel.opponent_id.isnot(None),
            )
            .all()
        )

    def list_incoming_challenges(self, user_id: int) -> List[ChallengeModel]:
        return (
            self.session.query(ChallengeModel)
            .filter(ChallengeModel.opponent_id == user_id)
            .all()
        )

    def create_challenge(
        self,
        challenge: Challenge,
        game: GameModel,
        creator_id: int,
        opponent_id: int = None,
    ) -> ChallengeModel:
        challenge = ChallengeModel(
            game=game,
            creator_id=creator_id,
            opponent_id=opponent_id,
            creator_color=challenge.creator_color,
            min_rating=challenge.min_rating,
            max_rating=challenge.max_rating,
        )
        self.session.add(challenge)
        self.session.flush()
        return challenge

    def start_game(self, challenge: ChallengeModel, opponent_id: int):
        if challenge.opponent_id and challenge.opponent_id != opponent_id:
            raise Exception("Wrong opponent")

        game = challenge.game
        creator = self.get_user_by_id(challenge.creator_id)
        opponent = self.get_user_by_id(opponent_id)

        if challenge.creator_color is Color.BLACK:
            black, white = creator, opponent
        elif challenge.creator_color is Color.WHITE:
            black, white = opponent, creator
        elif challenge.creator_color is Color.NIGIRI:
            black, white = random.sample([creator, opponent], 2)
        else:
            black, white = sorted([creator, opponent], key=lambda user: user.rating)

        black_player = GamePlayerModel(
            game=game,
            user=black,
            color=Color.BLACK,
            time_left=game.initial_time,
        )
        white_player = GamePlayerModel(
            game=game,
            user=white,
            color=Color.WHITE,
            time_left=game.initial_time,
        )
        self.session.add_all([black_player, white_player])
        self.session.delete(challenge)

        return game
