from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from config import DATABASE_URI
from explorebaduk.database.base import BaseModel


class DatabaseHandler:
    def __init__(self, database_uri: str):
        self.engine = create_engine(database_uri)
        self.session = Session(self.engine)

    def query(self, model: BaseModel, **filters):
        query = self.session.query(model)

        if filters:
            query = query.filter_by(**filters)

        return query

    def fetch_one(self, model: BaseModel, **filters):
        return self.query(model, **filters).first()


db = DatabaseHandler(DATABASE_URI)
