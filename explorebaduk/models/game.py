from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .base import BaseModel


class GameModel(BaseModel):
    __tablename__ = "games"

    game_id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False)

    board_width = Column(Integer, nullable=False)
    board_height = Column(Integer, nullable=False)

    created_at = Column(DateTime)
    started_at = Column(DateTime)
    finished_at = Column(DateTime)

    sgf = Column(Text)

    players = relationship("GamePlayerModel", back_populates="game")


class GamePlayerModel(BaseModel):
    __tablename__ = "game_players"

    timer_id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey("games.game_id"))
    player_id = Column(Integer, ForeignKey("users.user_id"))

    time_system = Column(Integer, nullable=False)
    main_time = Column(Integer, default=0)
    overtime = Column(Integer, default=0)
    periods = Column(Integer, default=1)
    stones = Column(Integer, default=1)
    bonus = Column(Integer, default=0)

    time_left = Column(Integer)

    game = relationship("GameModel", back_populates="players")
