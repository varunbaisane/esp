import pytest # pyrefly: ignore [missing-import]
from datetime import datetime, timezone, timedelta # pyrefly: ignore [missing-import]
from unittest.mock import patch # pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session # pyrefly: ignore [missing-import]
from sqlalchemy import delete # pyrefly: ignore [missing-import]

from app.models.verification_otp import VerificationOTP, OTPPurpose
from app.models.user import User
from app.services.verification_service import VerificationService
from app.exceptions.auth import InvalidOTPError, OTPExpiredError, RateLimitExceededError
from app.core.security import hash_password

@pytest.fixture
def test_user(db: Session):
    user = User(
        email="verify_service@example.com",
        full_name="Verify User",
        hashed_password=hash_password("password"),
        email_verified=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.execute(delete(VerificationOTP).where(VerificationOTP.user_id == user.id))
    db.delete(user)
    db.commit()

def test_otp_hashing():
    service = VerificationService()
    otp_val = "123456"
    hash1 = service._hash_otp(otp_val)
    hash2 = service._hash_otp(otp_val)
    assert hash1 == hash2
    assert hash1 != otp_val
    assert len(hash1) == 64  # SHA256 hex string length

def test_create_and_verify_otp(db: Session, test_user: User):
    service = VerificationService()
    otp_value = service.create_otp(db, test_user.id, OTPPurpose.EMAIL_VERIFICATION)
    assert len(otp_value) == 6
    assert otp_value.isdigit()
    
    # Verify success
    service.verify_otp(db, test_user.id, OTPPurpose.EMAIL_VERIFICATION, otp_value)
    
    # Ensure it's marked as consumed
    otp_record = db.query(VerificationOTP).filter_by(user_id=test_user.id).first()
    assert otp_record.consumed_at is not None

def test_verify_consumed_otp_fails(db: Session, test_user: User):
    service = VerificationService()
    otp_value = service.create_otp(db, test_user.id, OTPPurpose.EMAIL_VERIFICATION)
    
    # First verification succeeds
    service.verify_otp(db, test_user.id, OTPPurpose.EMAIL_VERIFICATION, otp_value)
    
    # Second verification fails
    with pytest.raises(InvalidOTPError):
        service.verify_otp(db, test_user.id, OTPPurpose.EMAIL_VERIFICATION, otp_value)

def test_verify_invalid_otp(db: Session, test_user: User):
    service = VerificationService()
    service.create_otp(db, test_user.id, OTPPurpose.EMAIL_VERIFICATION)
    
    with pytest.raises(InvalidOTPError):
        service.verify_otp(db, test_user.id, OTPPurpose.EMAIL_VERIFICATION, "000000")

def test_verify_expired_otp(db: Session, test_user: User):
    service = VerificationService()
    otp_value = service.create_otp(db, test_user.id, OTPPurpose.EMAIL_VERIFICATION)
    
    # Manually expire the OTP
    otp_record = db.query(VerificationOTP).filter_by(user_id=test_user.id).first()
    otp_record.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    db.commit()
    
    with pytest.raises(OTPExpiredError):
        service.verify_otp(db, test_user.id, OTPPurpose.EMAIL_VERIFICATION, otp_value)

def test_purpose_mismatch(db: Session, test_user: User):
    service = VerificationService()
    otp_value = service.create_otp(db, test_user.id, OTPPurpose.EMAIL_VERIFICATION)
    
    # Try verifying with PASSWORD_RESET purpose
    with pytest.raises(InvalidOTPError):
        service.verify_otp(db, test_user.id, OTPPurpose.PASSWORD_RESET, otp_value)

def test_resend_invalidates_previous_otp(db: Session, test_user: User):
    service = VerificationService()
    # Need to bypass rate limiting for this test
    with patch.object(service, 'enforce_rate_limits', return_value=None):
        otp1 = service.create_otp(db, test_user.id, OTPPurpose.EMAIL_VERIFICATION)
        otp2 = service.create_otp(db, test_user.id, OTPPurpose.EMAIL_VERIFICATION)
        
        # OTP 1 should now be deleted/invalidated
        with pytest.raises(InvalidOTPError):
            service.verify_otp(db, test_user.id, OTPPurpose.EMAIL_VERIFICATION, otp1)
            
        # OTP 2 should work
        service.verify_otp(db, test_user.id, OTPPurpose.EMAIL_VERIFICATION, otp2)

def test_rate_limiting(db: Session, test_user: User):
    service = VerificationService()
    
    # First request works
    service.create_otp(db, test_user.id, OTPPurpose.EMAIL_VERIFICATION)
    
    # Second request within a minute fails
    with pytest.raises(RateLimitExceededError, match="1 minute"):
        service.create_otp(db, test_user.id, OTPPurpose.EMAIL_VERIFICATION)
        
    # Simulate time passing (1 min) but within 1 hour
    otp_record = db.query(VerificationOTP).filter_by(user_id=test_user.id).first()
    otp_record.created_at = datetime.now(timezone.utc) - timedelta(minutes=2)
    db.commit()
    
    # Create 4 more OTPs (total 5)
    for _ in range(4):
        with patch.object(service, 'generate_otp', return_value="123456"):
            # We mock enforce_rate_limits to quickly seed the DB for the 1 hour test
            pass
        
    # Manually seed 5 OTPs within the last hour
    db.execute(delete(VerificationOTP).where(VerificationOTP.user_id == test_user.id))
    for _ in range(5):
        record = VerificationOTP(
            user_id=test_user.id,
            otp_hash="hash",
            purpose=OTPPurpose.EMAIL_VERIFICATION,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
            created_at=datetime.now(timezone.utc) - timedelta(minutes=10) # 10 mins ago, bypassing 1 min limit
        )
        db.add(record)
    db.commit()

    # The 6th request fails for the hourly limit
    with pytest.raises(RateLimitExceededError, match="hour"):
        service.create_otp(db, test_user.id, OTPPurpose.EMAIL_VERIFICATION)
