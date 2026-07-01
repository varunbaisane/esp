from fastapi.testclient import TestClient # pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session # pyrefly: ignore [missing-import]
from datetime import datetime, timezone

from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.repositories import UserRoleRepository

def test_user_state_changes_reflect_in_me_endpoint(client: TestClient, db: Session):
    """
    Test that assigning or removing a role dynamically changes the
    pending_approval and can_access_application flags in the /me endpoint
    without needing a new JWT.
    """
    # 1. Create a user who is verified but has no roles
    user = User(
        email="test_onboarding@esp.com",
        full_name="Test Onboarding",
        hashed_password="hashed_password",
        email_verified=True,
        email_verified_at=datetime.now(timezone.utc)
    )
    db.add(user)
    
    # Ensure SUPPORT_L1 role exists
    role = db.query(Role).filter_by(name="SUPPORT_L1").first()
    if not role:
        role = Role(name="SUPPORT_L1")
        db.add(role)

    db.commit()
    db.refresh(user)
    db.refresh(role)

    headers = {"Authorization": f"Bearer testuser_{user.id}"}
    user_role_repo = UserRoleRepository(db)

    # User is pending
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["pending_approval"] is True
    assert data["can_access_application"] is False
    assert data["roles"] == []

    # 2. Manager (or Admin) assigns a role
    user_role = UserRole(user_id=user.id, role_id=role.id)
    user_role_repo.assign(user_role)
    db.commit()

    # User is now active (without re-logging in)
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["pending_approval"] is False
    assert data["can_access_application"] is True
    assert "SUPPORT_L1" in data["roles"]

    # 3. Manager removes the role
    user_role_to_remove = user_role_repo.get_assignment(user.id, role.id)
    if user_role_to_remove:
        db.delete(user_role_to_remove)
        db.commit()

    # User is pending again (without re-logging in)
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["pending_approval"] is True
    assert data["can_access_application"] is False
    assert data["roles"] == []
