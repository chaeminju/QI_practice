import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL")

engine = create_engine(DATABASE_URL, pool_pre_ping=True) if DATABASE_URL else None
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) if engine else None


class Base(DeclarativeBase):
    pass


def get_db():
    if SessionLocal is None:
        raise RuntimeError("DATABASE_URL is not set")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
