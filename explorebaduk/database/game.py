import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text


from explorebaduk.database.base import BaseModel


class GameModel(BaseModel):
    # name
    # board size
    # time settings
    # player ids
    # time settings
    # flags (!)
    # game type (!)

    __tablename__ = "games"

    game_id = Column(Integer, primary_key=True)
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    finished_at = Column(DateTime)

    name = Column(String, nullable=False)

    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)

    sgf = Column(Text, name="SGF")

    timers = relationship("TokenModel", back_populates="game")
