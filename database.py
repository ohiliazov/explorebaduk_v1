from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    email = Column(String(255))
    password = Column(String(255))


class SignInToken(Base):
    __tablename__ = 'signin_tokens'

    user_id = Column(Integer, primary_key=True)
    token = Column(String(64))


if __name__ == '__main__':
    from sqlalchemy.engine import create_engine
    from sqlalchemy.orm import sessionmaker
    from config import DevConfig

    engine = create_engine(DevConfig.SQLALCHEMY_URL)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    session.execute('DELETE FROM users;')
    session.execute('DELETE FROM signin_tokens;')

    for i in range(100):
        user = User(user_id=i, email=f'test{i}@test.test', password='test')
        token = SignInToken(user_id=i, token=f'token_{i}')

        session.add(user)
        session.add(token)

    session.commit()
    session.close()
