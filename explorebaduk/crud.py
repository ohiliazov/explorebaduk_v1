import datetime

from .database import scoped_session
from .models import TokenModel, UserModel


def get_user_by_token(token) -> UserModel:
    with scoped_session() as session:
        auth_token = (
            session.query(TokenModel)
            .filter(
                TokenModel.token == token,
                TokenModel.expire >= datetime.datetime.utcnow(),
            )
            .first()
        )

        if auth_token:
            return auth_token.user
