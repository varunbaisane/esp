from typing import Generator

from sqlalchemy import create_engine  # pyrefly: ignore [missing-import]
from sqlalchemy.orm import sessionmaker, Session  # pyrefly: ignore [missing-import]

from app.core.config import db_settings

engine = create_engine(
    db_settings.DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """Yield a database session and ensure cleanup after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
