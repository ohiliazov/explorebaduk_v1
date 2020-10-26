from contextlib import contextmanager
from sqlalchemy.orm import create_session

from explorebaduk.database import UserModel, TokenModel


@contextmanager
def scoped_session(request):
    session = create_session(bind=request.app.db_engine, autocommit=False)
    try:
        yield session
        session.commit()
    except Exception as ex:
        session.rollback()
        raise ex
    finally:
        session.close()


def get_player_by_id(request, player_id: int) -> UserModel:
    with scoped_session(request) as session:
        return session.query(UserModel).get(player_id)


def get_user_by_token(request) -> UserModel:
    token = request.headers.get("Authorization")
    with scoped_session(request) as session:
        auth_token = session.query(TokenModel).filter_by(token=token).first()

        if auth_token:
            return auth_token.user
