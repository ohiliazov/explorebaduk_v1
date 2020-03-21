from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from config import DATABASE_URI
from explorebaduk.database.base import BaseModel
from explorebaduk.database.token import TokenModel
from explorebaduk.database.user import UserModel
from explorebaduk.database.game import GameModel
from explorebaduk.database.timer import TimerModel


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

    def get_or_create(self, model: BaseModel, key, **data):
        result = self.fetch_one(model)
        if not result:
            model_instance = model(key **data)
            self.session.add(model_instance)


db = DatabaseHandler(DATABASE_URI)
