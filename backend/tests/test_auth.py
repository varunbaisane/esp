import pytest # pyrefly: ignore [missing-import]
from unittest.mock import patch
from datetime import datetime, timezone, timedelta
from jose import jwt

from app.models.user import User
from app.models.verification_otp import VerificationOTP, OTPPurpose
from app.core.auth_config import auth_settings

# Ensure no emails are actually sent during tests
@pytest.fixture(autouse=True)
def mock_email_service():
    with patch("app.services.email_service.EmailService") as mock:
        yield mock

def test_registration_success(client, db, mock_email_service):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "register@test.com", "full_name": "Test Reg", "password": "Password123!"}
    )
    assert response.status_code == 201
    mock_email_service.return_value.send.assert_called_once()
    
    # Contract validation
    data = response.json()
    assert data["verification_required"] is True
    
    # DB validation
    user = db.query(User).filter_by(email="register@test.com").first()
    assert user is not None
    assert user.email_verified is False
    assert user.is_system_account is False
    
    # OTP validation
    otp = db.query(VerificationOTP).filter_by(user_id=user.id, purpose=OTPPurpose.EMAIL_VERIFICATION).first()
    assert otp is not None
    assert otp.consumed_at is None

@pytest.mark.parametrize("bad_password", [
    "abc",
    "PASSWORD",
    "Password",
    "Password1",
    "Password!",
])
def test_registration_password_validation(client, bad_password):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": f"bad_{bad_password}@test.com", "full_name": "Bad Pass", "password": bad_password}
    )
    assert response.status_code == 422

def test_registration_duplicate_email(client, db):
    client.post(
        "/api/v1/auth/register",
        json={"email": "dup@test.com", "full_name": "Test Dup", "password": "Password123!"}
    )
    
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "dup@test.com", "full_name": "Test Dup 2", "password": "Password123!"}
    )
    assert response.status_code == 409
    assert "already registered" in response.json()["detail"]

def test_login_unverified_rejected(client, db):
    client.post(
        "/api/v1/auth/register",
        json={"email": "login_unverified@test.com", "full_name": "Test Unverified", "password": "Password123!"}
    )
    
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "login_unverified@test.com", "password": "Password123!", "remember_me": False}
    )
    assert response.status_code == 403
    assert "email address not verified" in response.json()["detail"].lower()

@pytest.fixture
def verified_user(client, db):
    # Register
    client.post(
        "/api/v1/auth/register",
        json={"email": "verified@test.com", "full_name": "Verified", "password": "Password123!"}
    )
    # Hack DB to verify directly for login tests
    user = db.query(User).filter_by(email="verified@test.com").first()
    user.email_verified = True
    user.email_verified_at = datetime.now(timezone.utc)
    db.commit()
    return user

def test_login_success_and_jwt_claims(client, verified_user):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "verified@test.com", "password": "Password123!", "remember_me": False}
    )
    assert response.status_code == 200
    
    # Contract validation
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    # JWT Claims Validation
    token = data["access_token"]
    payload = jwt.decode(token, auth_settings.SECRET_KEY, algorithms=[auth_settings.ALGORITHM])
    assert payload["sub"] == str(verified_user.id)
    # Ensure short expiry (not remember me)
    exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    assert exp_time < datetime.now(timezone.utc) + timedelta(minutes=auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES + 1)

    # Signature rejection
    bad = token[:-3] + "abc"
    from jose.exceptions import JWTError
    with pytest.raises(JWTError):
        jwt.decode(
            bad,
            auth_settings.SECRET_KEY,
            algorithms=[auth_settings.ALGORITHM],
        )

def test_login_remember_me_jwt_claims(client, verified_user):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "verified@test.com", "password": "Password123!", "remember_me": True}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    payload = jwt.decode(token, auth_settings.SECRET_KEY, algorithms=[auth_settings.ALGORITHM])
    exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    now = datetime.now(timezone.utc)
    from app.core.email_config import email_settings
    expected = email_settings.REMEMBER_ME_EXPIRE_DAYS
    assert timedelta(days=expected - 1) < (exp_time - now) < timedelta(days=expected + 1)

def test_login_wrong_password(client, verified_user):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "verified@test.com", "password": "WrongPassword1!", "remember_me": False}
    )
    assert response.status_code == 401

def test_forgot_password_generic_response(client, db):
    # Should always return 200 generic message
    response = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "nonexistent@test.com"}
    )
    assert response.status_code == 200
    assert "If the email exists" in response.json()["detail"]
    
def test_forgot_password_creates_otp(client, verified_user, db):
    response = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "verified@test.com"}
    )
    assert response.status_code == 200
    assert "If the email exists" in response.json()["detail"]
    
    otp = db.query(VerificationOTP).filter_by(
        user_id=verified_user.id, purpose=OTPPurpose.PASSWORD_RESET, consumed_at=None
    ).first()
    assert otp is not None

def test_email_verification_success(client, db):
    # Needs to bypass the random generation to get the exact OTP code,
    # or we can mock generate_otp
    with patch("app.services.verification_service.VerificationService.generate_otp", return_value="123456"):
        client.post(
            "/api/v1/auth/register",
            json={"email": "verify_me@test.com", "full_name": "To Verify", "password": "Password123!"}
        )
    
    response = client.post(
        "/api/v1/auth/verify-email",
        json={"email": "verify_me@test.com", "otp": "123456"}
    )
    assert response.status_code == 200
    assert "successfully verified" in response.json()["detail"]
    
    user = db.query(User).filter_by(email="verify_me@test.com").first()
    assert user.email_verified is True

def test_email_verification_invalid_otp(client, db):
    client.post(
        "/api/v1/auth/register",
        json={"email": "verify_fail@test.com", "full_name": "To Fail", "password": "Password123!"}
    )
    response = client.post(
        "/api/v1/auth/verify-email",
        json={"email": "verify_fail@test.com", "otp": "999999"}
    )
    assert response.status_code == 400
    assert "Invalid OTP" in response.json()["detail"]

def test_reset_password_success(client, db, verified_user):
    with patch("app.services.verification_service.VerificationService.generate_otp", return_value="654321"):
        client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "verified@test.com"}
        )
    
    response = client.post(
        "/api/v1/auth/reset-password",
        json={"email": "verified@test.com", "otp": "654321", "new_password": "NewPassword123!"}
    )
    assert response.status_code == 200
    assert "Password successfully reset." in response.json()["detail"]
    
    # Verify login works with new password
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "verified@test.com", "password": "NewPassword123!", "remember_me": False}
    )
    assert login_resp.status_code == 200
    
    # Old password fails
    login_resp_old = client.post(
        "/api/v1/auth/login",
        json={"email": "verified@test.com", "password": "Password123!", "remember_me": False}
    )
    assert login_resp_old.status_code == 401
