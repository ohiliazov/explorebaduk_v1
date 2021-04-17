from datetime import datetime
from typing import List

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

from .database import BaseModel
from .schemas import Color, GameSpeed, GameType, Rules


class UserModel(BaseModel):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    first_name = Column(String(60), nullable=False)
    last_name = Column(String(60), nullable=False)
    email = Column(String(255), nullable=False)
    username = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    rating = Column(Numeric(10), default=10)
    puzzle_rating = Column(Numeric(10), default=0)
    country = Column(String(255))
    avatar = Column(String(255))

    tokens: List["TokenModel"] = relationship(
        "TokenModel",
        back_populates="user",
        lazy="subquery",
    )
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

    sent_requests: List["GameRequestModel"] = relationship(
        "GameRequestModel",
        back_populates="creator",
        foreign_keys="GameRequestModel.creator_id",
        lazy="subquery",
    )

    received_requests: List["GameRequestModel"] = relationship(
        "GameRequestModel",
        back_populates="opponent",
        foreign_keys="GameRequestModel.opponent_id",
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
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    friend_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
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
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    blocked_user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    user: UserModel = relationship(
        "UserModel",
        back_populates="blocked_users",
        foreign_keys="BlacklistModel.user_id",
    )


class TokenModel(BaseModel):
    __tablename__ = "signin_tokens"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    token = Column(String(64))
    expire = Column(DateTime, nullable=True)

    user: UserModel = relationship(
        "UserModel",
        back_populates="tokens",
        lazy="subquery",
    )

    def __str__(self):
        return f"Token(user_id={self.user_id}, token={self.token})"

    def is_active(self):
        return self.expire is None or self.expire >= datetime.utcnow()


class GameRequestModel(BaseModel):
    __tablename__ = "game_requests"

    id = Column(Integer, primary_key=True)
    creator_id = Column(Integer, ForeignKey("users.user_id"))
    opponent_id = Column(Integer, ForeignKey("users.user_id"))
    game_setup = Column(JSON)

    creator: UserModel = relationship(
        "UserModel",
        back_populates="sent_requests",
        foreign_keys="GameRequestModel.creator_id",
        lazy="subquery",
    )

    opponent: UserModel = relationship(
        "UserModel",
        back_populates="received_requests",
        foreign_keys="GameRequestModel.opponent_id",
        lazy="subquery",
    )

    def as_dict(self):
        return {
            "creator_id": self.creator_id,
            "opponent_id": self.opponent_id,
            "game_setup": self.game_setup,
        }


class GameModel(BaseModel):
    __tablename__ = "games"

    game_id = Column(Integer, primary_key=True)

    started_at = Column(DateTime)
    finished_at = Column(DateTime)

    name = Column(String(255))
    rules = Column(Enum(Rules))
    game_type = Column(Enum(GameType))
    category = Column(Enum(GameSpeed))

    board_size = Column(Integer)
    handicap = Column(Integer)
    komi = Column(Numeric)

    time_settings = Column(JSON)
    sgf = Column(Text)

    result = Column(String(255))

    players = relationship("GamePlayerModel", back_populates="game")

    def as_dict(self, with_sgf: bool = False):
        game = {
            "game_id": self.game_id,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "name": self.name,
            "rules": self.rules,
            "game_type": self.game_type,
            "category": self.category,
            "board_size": self.board_size,
            "handicap": self.handicap,
            "komi": self.komi,
            "time_settings": self.time_settings,
        }
        if with_sgf:
            game["sgf"] = self.sgf


class GamePlayerModel(BaseModel):
    __tablename__ = "game_players"

    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey("games.game_id"))
    user_id = Column(Integer, ForeignKey("users.user_id"))
    color = Column(Enum(Color))
    time_left = Column(Numeric)

    game: GameModel = relationship("GameModel", back_populates="players")
