from fastapi import APIRouter, Depends, HTTPException, status # pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session # pyrefly: ignore [missing-import] 
import smtplib 

from app.api.deps import get_db
from app.api.deps.auth import get_current_user
from app.models import User
from app.schemas.auth import (
    RegisterRequest, LoginRequest, TokenResponse, CurrentUserResponse, RegisterResponse,
    SendOTPRequest, VerifyOTPRequest, ResetPasswordRequest
)
from app.schemas.user import UserRead
from app.repositories import UserRoleRepository
from app.services.auth_service import AuthService
from app.exceptions.auth import EmailAlreadyRegisteredError, InvalidCredentialsError, UnverifiedEmailError
from app.core.jwt import create_access_token

router = APIRouter()
auth_service = AuthService()

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user and send verification email.
    """
    from app.services.verification_service import VerificationService
    from app.models.verification_otp import OTPPurpose
    from app.services.email_service import EmailService

    try:
        user = auth_service.register_user(db, data)
        otp = VerificationService().create_otp(db, user.id, OTPPurpose.EMAIL_VERIFICATION)
        
        try:
            EmailService.send_verification_otp(user.email, otp)
        except Exception as e:
            db.delete(user)
            db.commit()
            raise HTTPException(status_code=500, detail="Unable to send verification email. Please try again later.")
            
        db.commit()
        
        return RegisterResponse(verification_required=True, email=user.email)
    except EmailAlreadyRegisteredError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

@router.post("/login", response_model=TokenResponse)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return an access token.
    """
    try:
        user = auth_service.authenticate_user(db, data)
        
        expires_delta = None
        if data.remember_me:
            from datetime import timedelta
            from app.core.email_config import email_settings
            expires_delta = timedelta(days=email_settings.REMEMBER_ME_EXPIRE_DAYS)
            
        token = create_access_token(subject=str(user.id), expires_delta=expires_delta)
        return TokenResponse(access_token=token)
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    except UnverifiedEmailError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email address not verified."
        )

@router.post("/send-verification-otp")
def send_verification_otp(
    data: SendOTPRequest,
    db: Session = Depends(get_db)
):
    from app.services.verification_service import VerificationService
    from app.models.verification_otp import OTPPurpose
    from app.services.email_service import EmailService
    from app.repositories.user_repository import UserRepository
    
    user = UserRepository(db).get_by_email(data.email)
    if not user or user.email_verified:
        return {"detail": "If the email is registered and unverified, an OTP will be sent."}
        
    try:
        otp = VerificationService().create_otp(db, user.id, OTPPurpose.EMAIL_VERIFICATION)
        EmailService.send_verification_otp(user.email, otp)
        db.commit()
    except Exception:
        pass
        
    return {"detail": "If the email is registered and unverified, an OTP will be sent."}

@router.post("/verify-email")
def verify_email(
    data: VerifyOTPRequest,
    db: Session = Depends(get_db)
):
    from app.services.verification_service import VerificationService
    from app.models.verification_otp import OTPPurpose
    from app.repositories.user_repository import UserRepository
    from app.exceptions.auth import InvalidOTPError, OTPExpiredError
    from datetime import datetime, timezone
    
    user = UserRepository(db).get_by_email(data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Verification session expired.\n\nPlease register again."
        )
        
    try:
        VerificationService().verify_otp(db, user.id, OTPPurpose.EMAIL_VERIFICATION, data.otp)
        user.email_verified = True
        user.email_verified_at = datetime.now(timezone.utc)
        db.commit()
        return {"detail": "Email successfully verified."}
    except OTPExpiredError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Verification code expired.\n\nRequest a new verification code."
        )
    except InvalidOTPError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/forgot-password")
def forgot_password(
    data: SendOTPRequest,
    db: Session = Depends(get_db)
):
    from app.services.verification_service import VerificationService
    from app.models.verification_otp import OTPPurpose
    from app.services.email_service import EmailService
    from app.repositories.user_repository import UserRepository
    
    user = UserRepository(db).get_by_email(data.email)
    if not user:
        return {"detail": "If the email exists, a password reset OTP will be sent."}
        
    try:
        otp = VerificationService().create_otp(db, user.id, OTPPurpose.PASSWORD_RESET)
        EmailService.send_password_reset_otp(user.email, otp)
        db.commit()
    except Exception:
        pass
        
    return {"detail": "If the email exists, a password reset OTP will be sent."}

@router.post("/reset-password")
def reset_password(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    from app.services.verification_service import VerificationService
    from app.models.verification_otp import OTPPurpose
    from app.repositories.user_repository import UserRepository
    from app.exceptions.auth import InvalidOTPError, OTPExpiredError
    from app.core.security import hash_password
    
    user = UserRepository(db).get_by_email(data.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request")
        
    try:
        VerificationService().verify_otp(db, user.id, OTPPurpose.PASSWORD_RESET, data.otp)
        user.hashed_password = hash_password(data.new_password)
        db.commit()
        return {"detail": "Password successfully reset."}
    except (InvalidOTPError, OTPExpiredError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/me", response_model=CurrentUserResponse)
def get_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get current user profile including roles and state.
    """
    from app.services.user_state_service import UserStateService
    
    roles = UserRoleRepository(db).list_roles_for_user(current_user.id)
    role_names = [role.name for role in roles]
    
    state_service = UserStateService(db)
    
    return CurrentUserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        roles=role_names,
        pending_approval=state_service.is_pending_approval(current_user),
        can_access_application=state_service.can_access_application(current_user),
    )
