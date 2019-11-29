from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer


Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    email = Column(String(255))
    password = Column(String(255))


class SignInTokens(Base):
    __tablename__ = 'signin_tokens'

    user_id = Column(Integer, primary_key=True)
    token = Column(String(64))


if __name__ == '__main__':
    from sqlalchemy.engine import create_engine
    from config import DevConfig

    engine = create_engine(DevConfig.SQLALCHEMY_URL)
    Base.metadata.create_all(engine)
