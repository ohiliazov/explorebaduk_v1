import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import Session

BaseModel = declarative_base()


class UserModel(BaseModel):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    first_name = Column(String(60))
    last_name = Column(String(60))
    email = Column(String(255))
    rating = Column(String(10))
    puzzle_rating = Column(String(10))

    tokens = relationship('TokenModel', back_populates='user')

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class TokenModel(BaseModel):
    __tablename__ = 'signin_tokens'

    token_id = Column(Integer, primary_key=True, name='SignIn_Token_ID')
    user_id = Column(Integer, ForeignKey('users.user_id'))
    token = Column(String(64))
    expired_at = Column(DateTime)

    user = relationship('UserModel', back_populates='tokens')

    @property
    def is_active(self):
        return datetime.datetime.utcnow() < self.expired_at


class GameModel(BaseModel):
    __tablename__ = 'games'

    game_id = Column(Integer, primary_key=True)
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    finished_at = Column(DateTime)

    game_type = Column(String(255))

    sgf = Column(Text, name='SGF')


def create_session(database_uri, expire_on_commit=True):
    engine = create_engine(database_uri)
    session = Session(bind=engine, expire_on_commit=expire_on_commit)
    return session
