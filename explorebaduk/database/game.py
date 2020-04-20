from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship


from explorebaduk.database.base import BaseModel


class GameModel(BaseModel):
    __tablename__ = "games"

    game_id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False)

    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)

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
