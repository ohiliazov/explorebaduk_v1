from typing import List

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    Integer,
    Numeric,
    String,
    Text,
)

from .schemas import CreatorColor, GameSpeed, Rules

BaseModel = declarative_base()


class UserModel(BaseModel):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    first_name = Column(String(60), nullable=False)
    last_name = Column(String(60), nullable=False)
    email = Column(String(255), nullable=False)
    username = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    rating = Column(Numeric(10), default=10)
    puzzle_rating = Column(Numeric(10), default=0)
    country = Column(String(255))
    avatar = Column(String(255))

    friends: List["FriendshipModel"] = relationship(
        "FriendshipModel",
        back_populates="user",
        foreign_keys="FriendshipModel.user_id",
        lazy="subquery",
    )
    blocked_users: List["BlacklistModel"] = relationship(
        "BlacklistModel",
        back_populates="user",
        foreign_keys="BlacklistModel.user_id",
        lazy="subquery",
    )
    outgoing_challenges: List["ChallengeModel"] = relationship(
        "ChallengeModel",
        back_populates="creator",
        foreign_keys="ChallengeModel.creator_id",
        lazy="subquery",
    )
    incoming_challenges: List["ChallengeModel"] = relationship(
        "ChallengeModel",
        back_populates="opponent",
        foreign_keys="ChallengeModel.opponent_id",
        lazy="subquery",
    )

    def __str__(self):
        return f"User(user_id={self.user_id}, name={self.full_name})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def asdict(self):
        return {
            "user_id": self.user_id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "rating": round(self.rating, 2),
            "puzzle_rating": round(self.puzzle_rating, 2),
            "country": self.country,
            "avatar": self.avatar,
        }

    def is_friend(self, user_id: int):
        for friend in self.friends:
            if friend.friend_id == user_id:
                return True

        return False


class FriendshipModel(BaseModel):
    __tablename__ = "friends"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(UserModel.user_id), nullable=False)
    friend_id = Column(Integer, ForeignKey(UserModel.user_id), nullable=False)
    muted = Column(Boolean, default=False)

    user: UserModel = relationship(
        "UserModel",
        back_populates="friends",
        foreign_keys="FriendshipModel.user_id",
    )

    friend: UserModel = relationship(
        "UserModel",
        back_populates="friends",
        foreign_keys="FriendshipModel.friend_id",
    )


class BlacklistModel(BaseModel):
    __tablename__ = "blocked_users"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(UserModel.user_id), nullable=False)
    blocked_user_id = Column(Integer, ForeignKey(UserModel.user_id), nullable=False)

    user: UserModel = relationship(
        "UserModel",
        back_populates="blocked_users",
        foreign_keys="BlacklistModel.user_id",
    )


class GameModel(BaseModel):
    __tablename__ = "games"

    game_id = Column(Integer, primary_key=True)

    name = Column(String(255))
    private = Column(Boolean)
    ranked = Column(Boolean)
    board_size = Column(Integer)
    rules = Column(Enum(Rules))
    speed = Column(Enum(GameSpeed))
    initial_time = Column(Integer, nullable=True)
    time_control = Column(JSON)
    handicap = Column(Integer)
    komi = Column(Numeric)

    started_at = Column(DateTime)
    finished_at = Column(DateTime)

    result = Column(String(255))
    sgf = Column(Text)

    challenge: "ChallengeModel" = relationship("ChallengeModel", back_populates="game")
    players: List["GamePlayerModel"] = relationship(
        "GamePlayerModel",
        back_populates="game",
    )

    def asdict(self):
        return {
            "game_id": self.game_id,
            "name": self.name,
            "private": self.private,
            "ranked": self.ranked,
            "board_size": self.board_size,
            "rules": self.rules,
            "speed": self.speed,
            "time_control": self.time_control,
            "handicap": self.handicap,
            "komi": self.komi,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "result": self.result,
        }


class ChallengeModel(BaseModel):
    __tablename__ = "challenges"

    challenge_id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey(GameModel.game_id))
    creator_id = Column(Integer, ForeignKey(UserModel.user_id))
    opponent_id = Column(Integer, ForeignKey(UserModel.user_id))
    creator_color = Column(Enum(CreatorColor))
    min_rating = Column(Integer)
    max_rating = Column(Integer)

    created_at = Column(DateTime)

    creator: UserModel = relationship(
        UserModel,
        back_populates="outgoing_challenges",
        foreign_keys="ChallengeModel.creator_id",
    )
    opponent: UserModel = relationship(
        UserModel,
        back_populates="incoming_challenges",
        foreign_keys="ChallengeModel.opponent_id",
    )
    game: GameModel = relationship(
        GameModel,
        back_populates="challenge",
        lazy="subquery",
    )

    def asdict(self):
        return {
            "challenge_id": self.challenge_id,
            "creator_id": self.creator_id,
            "opponent_id": self.opponent_id,
            "creator_color": self.creator_color,
            "min_rating": self.min_rating,
            "max_rating": self.max_rating,
            "created_at": self.created_at,
            "game": self.game.asdict(),
        }


class GamePlayerModel(BaseModel):
    __tablename__ = "game_players"

    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey(GameModel.game_id))
    user_id = Column(Integer, ForeignKey(UserModel.user_id))
    color = Column(Enum(CreatorColor))
    time_left = Column(Numeric)

    game: GameModel = relationship("GameModel", back_populates="players")
    user: UserModel = relationship("UserModel")
