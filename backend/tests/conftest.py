import os
import pytest # pyrefly: ignore [missing-import]
from fastapi.testclient import TestClient # pyrefly: ignore [missing-import]
from sqlalchemy import create_engine, text # pyrefly: ignore [missing-import]
from sqlalchemy.orm import sessionmaker # pyrefly: ignore [missing-import]
from dotenv import load_dotenv # pyrefly: ignore [missing-import]

load_dotenv(".env.test")

from app.main import app
from app.db.session import get_db
from app.db.base import Base

engine = create_engine(os.environ.get("DATABASE_URL", "postgresql+psycopg://esp:esp@localhost:5433/esp_test_db"))
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    yield
    engine.dispose()

@pytest.fixture(autouse=True)
def clean_db():
    # Truncate tables before each test dynamically
    with engine.begin() as conn:
        tables = ", ".join(table.name for table in Base.metadata.sorted_tables)
        if tables:
            conn.execute(text(f"TRUNCATE TABLE {tables} CASCADE;"))
    yield


@pytest.fixture
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
