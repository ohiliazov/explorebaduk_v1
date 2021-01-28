import os
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine(os.getenv("DATABASE_URI"))
SessionLocal = sessionmaker(autocommit=True, autoflush=True, bind=engine)

BaseModel = declarative_base()


@contextmanager
def scoped_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
