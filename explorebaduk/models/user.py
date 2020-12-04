from sqlalchemy import Boolean, Column, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from explorebaduk.models.base import BaseModel


class UserModel(BaseModel):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, name="User_ID")
    first_name = Column(String(60), name="First_Name")
    last_name = Column(String(60), name="Last_Name")
    email = Column(String(255), name="Email")
    username = Column(String(255), name="Username")
    rating = Column(Numeric(10), name="Rating")
    puzzle_rating = Column(Numeric(10), name="Puzzle_rating")
    avatar = Column(String(255), name="Avatar")

    tokens = relationship("TokenModel", back_populates="user")
    friends = relationship("FriendModel", back_populates="user", foreign_keys="FriendModel.user_id", lazy="subquery")

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

    def get_friend_ids(self):
        return {friend.user_id for friend in self.friends}

    def is_friend(self, user_id: int):
        for friend in self.friends:
            if friend.friend_id == user_id:
                return True
        return False


class FriendModel(BaseModel):
    __tablename__ = "friends"

    id = Column(Integer, name="ID", primary_key=True)
    user_id = Column(Integer, ForeignKey("users.User_ID"), name="User_ID", nullable=False)
    friend_id = Column(Integer, ForeignKey("users.User_ID"), name="Friend_ID", nullable=False)

    # friend = Column(Boolean, name="Friend", default=False)
    # watched = Column(Boolean, name="Watched", default=False)
    muted = Column(Boolean, name="Muted", default=False)
    blocked = Column(Boolean, name="Blocked", default=False)

    user = relationship("UserModel", back_populates="friends", foreign_keys="FriendModel.user_id")
