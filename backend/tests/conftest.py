import os
import pytest # pyrefly: ignore [missing-import]
from fastapi.testclient import TestClient # pyrefly: ignore [missing-import]
from sqlalchemy import create_engine, text # pyrefly: ignore [missing-import]
from sqlalchemy.orm import sessionmaker # pyrefly: ignore [missing-import]
from dotenv import load_dotenv # pyrefly: ignore [missing-import]

load_dotenv(".env.test")

from fastapi import Request # pyrefly: ignore [missing-import]

from app.main import app
from app.db.session import get_db
from app.db.base import Base

engine = create_engine(os.environ.get("DATABASE_URL", "postgresql+psycopg://esp:esp_test_password@localhost:5433/esp_test_db"))
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    engine.dispose()

@pytest.fixture(autouse=True)
def clean_db():
    if engine.url.database != "esp_test_db":
        raise AssertionError(f"FATAL: Attempting to wipe non-test database! ({engine.url.database})")
    
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

    def override_get_current_user(request: Request):
        from app.models.user import User
        from app.models.role import Role
        from datetime import datetime, timezone
        
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer testuser_"):
            user_id = int(auth_header.replace("Bearer testuser_", ""))
            user = db.query(User).get(user_id)
            if user:
                return user
        
        # We need an admin role
        admin_role = db.query(Role).filter_by(name="ADMIN").first()
        if not admin_role:
            admin_role = Role(name="ADMIN")
            db.add(admin_role)
            db.commit()
            
        user = db.query(User).filter_by(email="test_admin@esp.com").first()
        if not user:
            user = User(
                email="test_admin@esp.com",
                full_name="Test Admin",
                hashed_password="hashed_password",
                email_verified=True,
                email_verified_at=datetime.now(timezone.utc),
                is_system_account=True
            )
            user.roles.append(admin_role)
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    from app.api.deps.auth import get_current_user
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
