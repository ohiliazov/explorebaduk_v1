from sqlalchemy import Boolean, Column, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from .base import BaseModel


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

    tokens = relationship("TokenModel", back_populates="user")
    friends = relationship("FriendModel", back_populates="user", foreign_keys="FriendModel.user_id", lazy="subquery")
    blocked_users = relationship(
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

    def get_friends_list(self):
        return {friend.user_id for friend in self.friends}

    def is_friend(self, user_id: int):
        for friend in self.friends:
            if friend.friend_id == user_id and friend.is_friend:
                return True
        return False


class FriendModel(BaseModel):
    __tablename__ = "friends"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    friend_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    muted = Column(Boolean, default=False)

    user = relationship("UserModel", back_populates="friends", foreign_keys="FriendModel.user_id")


class BlockedUserModel(BaseModel):
    __tablename__ = "blocked_users"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    blocked_user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    user = relationship("UserModel", back_populates="blocked_users", foreign_keys="BlockedUserModel.user_id")
