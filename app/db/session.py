from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(
    settings.database.url,
    pool_pre_ping=True,
    pool_size=settings.database.pool_size,
    max_overflow=settings.database.max_overflow
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()