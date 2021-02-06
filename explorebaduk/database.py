import os
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

BaseModel = declarative_base()
SessionLocal = sessionmaker(autocommit=True, autoflush=True)

if database_uri := os.getenv("DATABASE_URI"):
    engine = create_engine(database_uri)
    SessionLocal.configure(bind=engine)


@contextmanager
def scoped_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
