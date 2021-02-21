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
    friends: List["FriendModel"] = relationship(
        "FriendModel",
        back_populates="user",
        foreign_keys="FriendModel.user_id",
        lazy="subquery",
    )
    blocked_users: List["BlockedUserModel"] = relationship(
        "BlockedUserModel",
        back_populates="user",
        foreign_keys="BlockedUserModel.user_id",
        lazy="subquery",
    )

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def as_dict(self):
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


class FriendModel(BaseModel):
    __tablename__ = "friends"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    friend_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    muted = Column(Boolean, default=False)

    user: UserModel = relationship(
        "UserModel",
        back_populates="friends",
        foreign_keys="FriendModel.user_id",
    )


class BlockedUserModel(BaseModel):
    __tablename__ = "blocked_users"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    blocked_user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    user: UserModel = relationship(
        "UserModel",
        back_populates="blocked_users",
        foreign_keys="BlockedUserModel.user_id",
    )


class TokenModel(BaseModel):
    __tablename__ = "signin_tokens"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    token = Column(String(64))
    expire = Column(DateTime)

    user: UserModel = relationship(
        "UserModel",
        back_populates="tokens",
        lazy="subquery",
    )

    def is_active(self):
        return self.expire >= datetime.utcnow()


class GameModel(BaseModel):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True)
    started_at = Column(DateTime, server_default=func.now())
    finished_at = Column(DateTime)
    status = Column(String(255), default="Open")
    settings = Column(JSON)
    sgf = Column(Text)

    players = relationship("GamePlayerModel", back_populates="game")

    def as_dict(self):
        return {
            "id": self.id,
            "started_at": self.started_at.timestamp(),
            "finished_at": self.finished_at.timestamp() if self.finished_at else None,
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
