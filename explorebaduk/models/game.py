from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from .base import BaseModel


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

    game = relationship("GameModel", back_populates="players")
