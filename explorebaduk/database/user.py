from sqlalchemy import Column, String, Integer, Numeric
from sqlalchemy.orm import relationship

from explorebaduk.database.base import BaseModel


class PlayerModel(BaseModel):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    first_name = Column(String(60))
    last_name = Column(String(60))
    email = Column(String(255))
    rating = Column(Numeric(10))
    puzzle_rating = Column(Numeric(10))

    tokens = relationship("TokenModel", back_populates="player")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def as_dict(self):
        return {
            "player_id": self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "rating": round(self.rating, 2),
            "puzzle_rating": round(self.puzzle_rating, 2),
        }
