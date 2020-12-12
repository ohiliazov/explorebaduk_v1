from contextlib import contextmanager

from sqlalchemy.orm import create_session

from explorebaduk.models import TokenModel, UserModel


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


def get_user_by_token(request, token) -> UserModel:
    with scoped_session(request) as session:
        auth_token = session.query(TokenModel).filter_by(token=token).first()

        if auth_token:
            return auth_token.user
