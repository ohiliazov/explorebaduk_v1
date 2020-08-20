from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from explorebaduk.database.base import BaseModel


class PlayerModel(BaseModel):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    first_name = Column(String(60))
    last_name = Column(String(60))
    email = Column(String(255))
    rating = Column(String(10))
    puzzle_rating = Column(String(10))

    tokens = relationship("TokenModel", back_populates="player")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def as_dict(self):
        return {
            "user_id": self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "rating": self.rating,
            "puzzle_rating": self.puzzle_rating,
        }
