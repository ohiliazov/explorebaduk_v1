from sqlalchemy import Column, String, Integer, ForeignKey, create_engine
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    email = Column(String(255))
    password = Column(String(255))

    signin_tokens = relationship('SignInToken', back_populates="user")


class SignInToken(Base):
    __tablename__ = 'signin_tokens'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    token = Column(String(64))

    user = relationship('User', back_populates="signin_tokens")


class DatabaseWrapper:
    def __init__(self, database_uri):
        self.engine = create_engine(database_uri)
        self.session = sessionmaker(bind=self.engine)()

    def first(self, model, **filters):
        return self.session.query(model).filter_by(**filters).first()


if __name__ == '__main__':
    import config

    Session = sessionmaker()
    engine = create_engine(config.DATABASE_URI)
    session = Session(bind=engine)

    Base.metadata.create_all(engine)

    session.execute('DELETE FROM users;')
    session.execute('DELETE FROM signin_tokens;')

    for i in range(100):
        user = User(user_id=i, email=f'test{i}@test.test', password='test')
        token = SignInToken(user_id=i, token=f'token_{i}')

        session.add(user)
        session.add(token)

    session.commit()
    session.close()
