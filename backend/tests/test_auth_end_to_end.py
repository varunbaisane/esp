import pytest # pyrefly: ignore [missing-import]
from unittest.mock import patch

@pytest.fixture(autouse=True)
def mock_email_service():
    with patch("app.services.email_service.EmailService") as mock:
        yield mock

def test_journey_register_verify_login(client, db):
    # Register
    with patch("app.services.verification_service.VerificationService.generate_otp", return_value="111111"):
        reg_resp = client.post(
            "/api/v1/auth/register",
            json={"email": "journey1@test.com", "full_name": "Journey One", "password": "Password123!"}
        )
        assert reg_resp.status_code == 201
    
    # Try login before verify (fails)
    log_fail_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "journey1@test.com", "password": "Password123!", "remember_me": False}
    )
    assert log_fail_resp.status_code == 403
    
    # Verify Email
    ver_resp = client.post(
        "/api/v1/auth/verify-email",
        json={"email": "journey1@test.com", "otp": "111111"}
    )
    assert ver_resp.status_code == 200
    
    # Login succeeds
    log_succ_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "journey1@test.com", "password": "Password123!", "remember_me": False}
    )
    assert log_succ_resp.status_code == 200
    assert "access_token" in log_succ_resp.json()

def test_journey_register_forgot_reset_login(client, db):
    # Register
    with patch("app.services.verification_service.VerificationService.generate_otp", return_value="222222"):
        client.post(
            "/api/v1/auth/register",
            json={"email": "journey2@test.com", "full_name": "Journey Two", "password": "Password123!"}
        )
        # Verify immediately
        client.post(
            "/api/v1/auth/verify-email",
            json={"email": "journey2@test.com", "otp": "222222"}
        )
        
    # Forgot Password
    with patch("app.services.verification_service.VerificationService.generate_otp", return_value="333333"):
        fp_resp = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "journey2@test.com"}
        )
        assert fp_resp.status_code == 200
        
    # Reset Password
    rp_resp = client.post(
        "/api/v1/auth/reset-password",
        json={"email": "journey2@test.com", "otp": "333333", "new_password": "NewPassword!9"}
    )
    assert rp_resp.status_code == 200
    
    # Login with new password
    log_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "journey2@test.com", "password": "NewPassword!9", "remember_me": False}
    )
    assert log_resp.status_code == 200

def test_journey_register_cleanup_verify_fails(client, db):
    # Register
    with patch("app.services.verification_service.VerificationService.generate_otp", return_value="444444"):
        client.post(
            "/api/v1/auth/register",
            json={"email": "journey3@test.com", "full_name": "Journey Three", "password": "Password123!"}
        )
        
    # Artificially age the user to be expired
    from app.models.user import User
    from datetime import datetime, timezone, timedelta
    
    user = db.query(User).filter_by(email="journey3@test.com").first()
    user.created_at = datetime.now(timezone.utc) - timedelta(minutes=30)
    db.commit()
    
    # Run cleanup service
    from app.services.user_cleanup_service import UserCleanupService
    UserCleanupService().cleanup_expired_unverified_users(db)
    
    # Try login -> fails
    log_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "journey3@test.com", "password": "Password123!", "remember_me": False}
    )
    assert log_resp.status_code == 401

    # Try forgot password -> generic 200
    fp_resp = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "journey3@test.com"}
    )
    assert fp_resp.status_code == 200

    # Try verify email -> should fail
    ver_resp = client.post(
        "/api/v1/auth/verify-email",
        json={"email": "journey3@test.com", "otp": "444444"}
    )
    assert ver_resp.status_code == 400
    assert "session expired" in ver_resp.json()["detail"].lower()

def test_journey_register_resend_otp(client, db):
    # Register -> OTP1
    with patch("app.services.verification_service.VerificationService.generate_otp", return_value="555555"):
        client.post(
            "/api/v1/auth/register",
            json={"email": "journey4@test.com", "full_name": "Journey Four", "password": "Password123!"}
        )
        
    # Resend OTP -> OTP2 (Mocking rate limits for testing)
    with patch("app.services.verification_service.VerificationService.enforce_rate_limits", return_value=None):
        with patch("app.services.verification_service.VerificationService.generate_otp", return_value="666666"):
            client.post(
                "/api/v1/auth/send-verification-otp",
                json={"email": "journey4@test.com"}
            )
            
    # Verify only ONE active OTP exists
    from app.models.user import User
    from app.models.verification_otp import VerificationOTP, OTPPurpose
    user = db.query(User).filter_by(email="journey4@test.com").first()
    assert (
        db.query(VerificationOTP)
        .filter_by(
            user_id=user.id,
            purpose=OTPPurpose.EMAIL_VERIFICATION,
            consumed_at=None
        )
        .count()
        == 1
    )
            
    # Try verifying with Old OTP -> Fails
    ver1_resp = client.post(
        "/api/v1/auth/verify-email",
        json={"email": "journey4@test.com", "otp": "555555"}
    )
    assert ver1_resp.status_code == 400
    
    # Verify with New OTP -> Succeeds
    ver2_resp = client.post(
        "/api/v1/auth/verify-email",
        json={"email": "journey4@test.com", "otp": "666666"}
    )
    assert ver2_resp.status_code == 200
