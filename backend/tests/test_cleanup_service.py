import pytest # pyrefly: ignore [missing-import]
from datetime import datetime, timezone, timedelta # pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session # pyrefly: ignore [missing-import]
from unittest.mock import patch # pyrefly: ignore [missing-import]
from sqlalchemy import delete # pyrefly: ignore [missing-import]

from app.models.user import User
from app.models.verification_otp import VerificationOTP, OTPPurpose
from app.services.user_cleanup_service import UserCleanupService
from app.core.security import hash_password

@pytest.fixture
def cleanup_users(db: Session):
    users_to_cleanup = []
    
    # 1. Stale unverified user (should be deleted)
    stale_user = User(
        email="stale@cleanup.com",
        full_name="Stale User",
        hashed_password=hash_password("password"),
        email_verified=False,
        is_system_account=False,
        created_at=datetime.now(timezone.utc) - timedelta(minutes=30)
    )
    users_to_cleanup.append(stale_user)
    
    # 2. Recent unverified user (should be kept)
    recent_user = User(
        email="recent@cleanup.com",
        full_name="Recent User",
        hashed_password=hash_password("password"),
        email_verified=False,
        is_system_account=False,
        created_at=datetime.now(timezone.utc) - timedelta(minutes=5)
    )
    users_to_cleanup.append(recent_user)
    
    # 3. Stale verified user (should be kept)
    verified_user = User(
        email="verified@cleanup.com",
        full_name="Verified User",
        hashed_password=hash_password("password"),
        email_verified=True,
        is_system_account=False,
        created_at=datetime.now(timezone.utc) - timedelta(minutes=30)
    )
    users_to_cleanup.append(verified_user)
    
    # 4. Stale system user (should be kept)
    system_user = User(
        email="system@cleanup.com",
        full_name="System User",
        hashed_password=hash_password("password"),
        email_verified=False,
        is_system_account=True,
        created_at=datetime.now(timezone.utc) - timedelta(minutes=30)
    )
    users_to_cleanup.append(system_user)

    # 5. Boundary user exact (should be kept)
    boundary_exact = User(
        email="exact@cleanup.com",
        full_name="Exact User",
        hashed_password=hash_password("password"),
        email_verified=False,
        is_system_account=False,
        created_at=datetime.now(timezone.utc) - timedelta(minutes=14, seconds=59)
    )
    users_to_cleanup.append(boundary_exact)

    # 6. Boundary user expired (should be deleted)
    boundary_expired = User(
        email="expired@cleanup.com",
        full_name="Expired User",
        hashed_password=hash_password("password"),
        email_verified=False,
        is_system_account=False,
        created_at=datetime.now(timezone.utc) - timedelta(minutes=15, seconds=1)
    )
    users_to_cleanup.append(boundary_expired)

    for u in users_to_cleanup:
        db.add(u)
    db.commit()
    
    for u in users_to_cleanup:
        db.refresh(u)
        
    # Add an OTP for the stale user to ensure cascade works
    otp = VerificationOTP(
        user_id=stale_user.id,
        otp_hash="testhash",
        purpose=OTPPurpose.EMAIL_VERIFICATION,
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=20)
    )
    db.add(otp)
    db.commit()
    
    ret = {
        "stale": stale_user.id,
        "recent": recent_user.id,
        "verified": verified_user.id,
        "system": system_user.id,
        "exact": boundary_exact.id,
        "expired": boundary_expired.id,
        "otp": otp.id
    }
    yield ret
    
    # Cleanup after
    user_ids = [ret[k] for k in ["stale", "recent", "verified", "system", "exact", "expired"]]
    db.execute(delete(VerificationOTP).where(VerificationOTP.user_id.in_(user_ids)))
    db.execute(delete(User).where(User.id.in_(user_ids)))
    db.commit()


def test_cleanup_deletes_only_stale_unverified(db: Session, cleanup_users: dict):
    service = UserCleanupService()
    users_deleted, otps_deleted = service.cleanup_expired_unverified_users(db)
    
    assert users_deleted == 2 # stale and boundary_expired
    assert otps_deleted == 1
    
    # Check DB state
    assert db.query(User).filter_by(id=cleanup_users["stale"]).first() is None
    assert db.query(User).filter_by(id=cleanup_users["expired"]).first() is None
    
    assert db.query(VerificationOTP).filter_by(id=cleanup_users["otp"]).first() is None
    
    assert db.query(User).filter_by(id=cleanup_users["recent"]).first() is not None
    assert db.query(User).filter_by(id=cleanup_users["verified"]).first() is not None
    assert db.query(User).filter_by(id=cleanup_users["system"]).first() is not None
    assert db.query(User).filter_by(id=cleanup_users["exact"]).first() is not None


def test_cleanup_transaction_rollback(db: Session, cleanup_users: dict):
    service = UserCleanupService()
    
    # Force a failure during deletion to ensure rollback
    original_delete = db.query(User).delete
    
    def failing_delete(*args, **kwargs):
        raise Exception("Simulated DB failure")
    
    with patch("sqlalchemy.orm.Query.delete", side_effect=failing_delete):
        with pytest.raises(Exception, match="Simulated DB failure"):
            service.cleanup_expired_unverified_users(db)
            
    # Everything should still be there because of the rollback
    assert db.query(User).filter_by(id=cleanup_users["stale"]).first() is not None
    assert db.query(VerificationOTP).filter_by(id=cleanup_users["otp"]).first() is not None
