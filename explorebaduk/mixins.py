from contextlib import contextmanager

from sqlalchemy.orm import create_session

from explorebaduk.database import PlayerModel, TokenModel


@contextmanager
def scoped_session(request):
    session = create_session(bind=request.app.db_engine, autocommit=False)
    try:
        yield session
        session.commit()
    except Exception as ex:
        session.rollback()
        raise DatabaseError from ex
    finally:
        session.close()


class DatabaseError(Exception):
    pass


class DatabaseMixin:

    @staticmethod
    def get_player_by_id(request, player_id: int) -> PlayerModel:
        with scoped_session(request) as session:
            return session.query(PlayerModel).get(player_id)

    @staticmethod
    def get_player_by_token(request) -> PlayerModel:
        token = request.headers.get("Authorization")
        with scoped_session(request) as session:
            auth_token = session.query(TokenModel).filter_by(token=token).first()

            if auth_token:
                return auth_token.player
