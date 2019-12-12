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


class GameModel(BaseModel):
    __tablename__ = 'games'

    game_id = Column(Integer, primary_key=True)
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    finished_at = Column(DateTime)

    game_type = Column(String(255))

    sgf = Column(Text, name='SGF')


def bind_engine(engine):
    BaseModel.metadata.bind = engine
    Session.configure(bind=engine)


def create_session(database_uri):
    engine = create_engine(database_uri)
    session = Session(bind=engine)
    return session


def create_test_database(database_uri):
    import fauxfactory
    import datetime

    session = create_session(database_uri)

    session.execute('DROP TABLE IF EXISTS users ;')
    session.execute('DROP TABLE IF EXISTS signin_tokens ;')

    BaseModel.metadata.create_all(session.bind)

    for i in range(100):
        user_data = {
            'user_id': i,
            'first_name': "John",
            'last_name': f"Doe#{i}",
            'email': fauxfactory.gen_email(name=f'johndoe{i}', domain='explorebaduk'),
            'rating': fauxfactory.gen_number(0, 3000),
            'puzzle_rating': fauxfactory.gen_number(0, 3000),
        }
        user = UserModel(**user_data)

        token_data = {
            'token_id': i,
            'user_id': i,
            # 'token': ''.join(random.choice(string.ascii_letters) for i in range(64)),
            'token': f'token_{i}',
            'expired_at': datetime.datetime.utcnow() + datetime.timedelta(minutes=10),
        }
        token = TokenModel(**token_data)

        session.add(user)
        session.add(token)

    session.commit()
    session.close()


if __name__ == '__main__':
    from explorebaduk import config

    create_test_database(config.DATABASE_URI)
