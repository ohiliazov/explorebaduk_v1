from datetime import datetime
from typing import List

from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import (
    JSON,
    Boolean,
    DateTime,
    Integer,
    Numeric,
    String,
    Text,
)

from .database import BaseModel


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


class GameModel(BaseModel):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, server_default=func.now())
    started_at = Column(DateTime)
    finished_at = Column(DateTime)
    status = Column(String(255))
    settings = Column(JSON)
    sgf = Column(Text)

    players = relationship("GamePlayerModel", back_populates="game")

    def as_dict(self):
        return {
            "id": self.id,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "status": self.status,
            "settings": self.settings,
            "sgf": self.sgf,
        }


class GamePlayerModel(BaseModel):
    __tablename__ = "game_players"

    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey("games.id"))
    user_id = Column(Integer, ForeignKey("users.user_id"))
    color = Column(String(255))
    time_left = Column(Numeric)

    game: GameModel = relationship("GameModel", back_populates="players")
