import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import Session

Base = declarative_base()


class UserModel(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, name='User_ID')
    first_name = Column(String(60), name='First_Name')
    last_name = Column(String(60), name='Last_Name')
    email = Column(String(255), name='Email')
    rating = Column(String(10), name='Rating')
    puzzle_rating = Column(String(10), name='Puzzle_rating')

    tokens = relationship('TokenModel', back_populates='user')


class TokenModel(Base):
    __tablename__ = 'signin_tokens'

    token_id = Column(Integer, primary_key=True, name='SignIn_Token_ID')
    user_id = Column(Integer, ForeignKey('users.User_ID'), name='User_ID')
    token = Column(String(64), name='Token')
    expired_at = Column(DateTime, name='Expired_At')

    user = relationship('UserModel', back_populates='tokens')


class GameModel(Base):
    __tablename__ = 'games'

    game_id = Column(Integer, primary_key=True, name='Game_ID')
    started_at = Column(DateTime, default=datetime.datetime.utcnow, name='Started_At')
    finished_at = Column(DateTime, name='Finished_At')

    game_type = Column(String(255), name='Game_Type')
    settings = Column()

    sgf = Column(Text, name='SGF')


def create_session(database_uri):
    engine = create_engine(database_uri)
    session = Session(bind=engine)
    return session


def create_test_database(database_uri):
    import string
    import random
    import fauxfactory
    import datetime

    session = create_session(database_uri)

    session.execute('DROP TABLE IF EXISTS users ;')
    session.execute('DROP TABLE IF EXISTS signin_tokens ;')

    Base.metadata.create_all(session.bind)

    for i in range(100):
        user_data = {
            'user_id': i,
            'first_name': fauxfactory.gen_alpha(random.randrange(1, 60)),
            'last_name': fauxfactory.gen_alpha(random.randrange(1, 60)),
            'email': fauxfactory.gen_email(name=f'user{i}', domain='explorebaduk'),
        }
        user = UserModel(**user_data)

        token_data = {
            'token_id': i,
            'user_id': i,
            'token': ''.join(random.choice(string.ascii_letters) for i in range(64)),
            'expired_at': datetime.datetime.utcnow() + datetime.timedelta(minutes=10),
        }
        token = TokenModel(**token_data)

        session.add(user)
        session.add(token)

    session.commit()
    session.close()


if __name__ == '__main__':
    import config

    create_test_database(config.DATABASE_URI)
