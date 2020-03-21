from sqlalchemy import Column, Integer

from explorebaduk.database.base import BaseModel


class TimerModel(BaseModel):
    __tablename__ = "timers"

    game_id = Column(Integer, primary_key=True)
    player_id = Column(Integer, primary_key=True)

    time_system = Column(Integer, nullable=False)

    main_time = Column(Integer)
    overtime = Column(Integer)
    periods = Column(Integer)
    stones = Column(Integer)
    bonus = Column(Integer)

    time_left = Column(Integer)
