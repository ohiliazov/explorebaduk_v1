import os

from sqlalchemy import Column, String, Integer, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


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


class DatabaseWrapper:
    def __init__(self, database_uri):
        self.engine = create_engine(database_uri)
        self.session = sessionmaker(bind=self.engine)()

    def first(self, model, **filters):
        return self.session.query(model).filter_by(**filters).first()


if __name__ == '__main__':
    from config import DevConfig

    db = DatabaseWrapper(DevConfig.DATABASE_URI)
    Base.metadata.create_all(db.engine)

    session = db.session
    db.session.execute('DELETE FROM users;')
    db.session.execute('DELETE FROM signin_tokens;')

    for i in range(100):
        user = User(user_id=i, email=f'test{i}@test.test', password='test')
        token = SignInToken(user_id=i, token=f'token_{i}')

        db.session.add(user)
        db.session.add(token)

    db.session.commit()
    db.session.close()
