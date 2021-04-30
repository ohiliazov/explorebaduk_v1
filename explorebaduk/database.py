import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import BaseModel

engine = create_engine(os.getenv("DATABASE_URI"))
Session = sessionmaker(engine, autocommit=True, expire_on_commit=False)


class DatabaseManager:
    def __init__(self):
        self.session = Session()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def add(self, instance: BaseModel) -> BaseModel:
        self.session.add(instance)
        self.session.flush()
        return instance
