from sqlalchemy import Column, String, Integer, Numeric
from sqlalchemy.orm import relationship

from explorebaduk.database.base import BaseModel


class UserModel(BaseModel):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, name="User_ID")
    first_name = Column(String(60), name="First_Name")
    last_name = Column(String(60), name="Last_Name")
    email = Column(String(255), name="Email")
    username = Column(String(255), name="Username")
    rating = Column(Numeric(10), name="Rating")
    puzzle_rating = Column(Numeric(10), name="Puzzle_rating")

    tokens = relationship("TokenModel", back_populates="user")

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
        }
