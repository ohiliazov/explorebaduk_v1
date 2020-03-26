from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from config import DATABASE_URI
from explorebaduk.database.base import BaseModel
from explorebaduk.database.token import TokenModel
from explorebaduk.database.user import UserModel
from explorebaduk.database.game import GameModel, GamePlayerModel


class DatabaseHandler:
    def __init__(self, database_uri: str):
        self.engine = create_engine(database_uri)
        self.session = Session(self.engine)

    def get_by_id(self, model: BaseModel, key):
        return self.session.query(model).get(key)

    def query(self, model: BaseModel, **filters):
        query = self.session.query(model)

        if filters:
            query = query.filter_by(**filters)

        return query

    def fetch_one(self, model: BaseModel, **filters):
        return self.query(model, **filters).first()

    def save(self, instance: BaseModel):
        self.session.add(instance)
        try:
            self.session.commit()
        except SQLAlchemyError:
            self.session.rollback()

    def delete(self, instance: BaseModel):
        self.session.delete(instance)
        try:
            self.session.commit()
        except SQLAlchemyError:
            self.session.rollback()


db = DatabaseHandler(DATABASE_URI)
