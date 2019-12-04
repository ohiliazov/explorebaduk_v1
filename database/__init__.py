from sqlalchemy import Column, String, Integer, ForeignKey
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

    tokens = relationship('TokenModel', back_populates='user')


class TokenModel(Base):
    __tablename__ = 'signin_tokens'

    token_id = Column(Integer, primary_key=True, name='SignIn_Token_ID')
    user_id = Column(Integer, ForeignKey('users.User_ID'))
    token = Column(String(64), name='Token')

    user = relationship('UserModel', back_populates='tokens')


def create_session(database_uri):
    engine = create_engine(database_uri)
    session = Session(bind=engine)
    return session


if __name__ == '__main__':
    import config
    import string
    import random

    session = create_session(config.DATABASE_URI)

    Base.metadata.create_all(session.bind)

    session.execute('DELETE FROM users;')
    session.execute('DELETE FROM signin_tokens;')

    for i in range(100):
        user_data = {'user_id': i,
                     'first_name': 'John',
                     'last_name': f'Doe#{i}',
                     'email': f'john.doe{i}@explorebaduk.test'}
        user = UserModel(**user_data)
        token = TokenModel(token_id=i, user_id=i, token=''.join(random.choice(string.ascii_letters) for i in range(64)))

        session.add(user)
        session.add(token)

    session.commit()
    session.close()
