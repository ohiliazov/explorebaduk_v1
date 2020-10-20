import asyncio
from sanic.log import logger
from sanic.websocket import WebSocketCommonProtocol
from contextlib import contextmanager

import simplejson as json
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
        raise DatabaseError from ex
    finally:
        session.close()


class DatabaseError(Exception):
    pass


class DatabaseMixin:
    @staticmethod
    def get_player_by_id(request, player_id: int) -> UserModel:
        with scoped_session(request) as session:
            return session.query(UserModel).get(player_id)

    @staticmethod
    def get_user_by_token(request) -> UserModel:
        token = request.headers.get("Authorization")
        with scoped_session(request) as session:
            auth_token = session.query(TokenModel).filter_by(token=token).first()

            if auth_token:
                return auth_token.user


class SubscriberMixin:
    ws_list: set

    def is_online(self) -> bool:
        return bool(self.ws_list)

    def subscribe(self, ws: WebSocketCommonProtocol):
        self.ws_list.add(ws)

    def unsubscribe(self, ws: WebSocketCommonProtocol):
        self.ws_list.remove(ws)

    async def send_json(self, data: dict):
        message = json.dumps(data)

        if self.ws_list:
            await asyncio.gather(*[ws.send(message) for ws in self.ws_list], return_exceptions=True)
            logger.info("> [send_json] %s", message)
