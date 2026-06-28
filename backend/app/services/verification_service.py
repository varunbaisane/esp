import secrets
import hashlib
import hmac
from datetime import datetime, timezone, timedelta
from typing import Tuple

from sqlalchemy import delete, and_  # pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session  # pyrefly: ignore [missing-import]

from app.models.verification_otp import VerificationOTP, OTPPurpose
from app.core.auth_config import auth_settings
from app.core.email_config import email_settings
from app.exceptions.auth import InvalidOTPError, OTPExpiredError, RateLimitExceededError


class VerificationService:
    def _hash_otp(self, otp: str) -> str:
        """Hash OTP using SHA256 with the app SECRET_KEY as a pepper."""
        msg = f"{auth_settings.SECRET_KEY}:{otp}".encode("utf-8")
        return hashlib.sha256(msg).hexdigest()

    def generate_otp(self) -> str:
        """Generate a random 6-digit numeric OTP."""
        return f"{secrets.randbelow(1000000):06d}"

    def enforce_rate_limits(self, db: Session, user_id: int, purpose: OTPPurpose) -> None:
        """
        Enforce rate limits:
        - Max 1 OTP generation per minute.
        - Max 5 OTP generations per hour.
        """
        now = datetime.now(timezone.utc)
        one_min_ago = now - timedelta(minutes=1)
        one_hour_ago = now - timedelta(hours=1)

        recent_otps = db.query(VerificationOTP).filter(
            VerificationOTP.user_id == user_id,
            VerificationOTP.purpose == purpose,
            VerificationOTP.created_at >= one_hour_ago
        ).order_by(VerificationOTP.created_at.desc()).all()

        if len(recent_otps) >= 5:
            raise RateLimitExceededError("Maximum OTP requests per hour exceeded.")

        if recent_otps and recent_otps[0].created_at >= one_min_ago:
            raise RateLimitExceededError("Please wait 1 minute before requesting another OTP.")

    def create_otp(self, db: Session, user_id: int, purpose: OTPPurpose) -> str:
        self.enforce_rate_limits(db, user_id, purpose)

        # Invalidate any existing active OTPs for this purpose
        db.execute(
            delete(VerificationOTP).where(
                and_(
                    VerificationOTP.user_id == user_id,
                    VerificationOTP.purpose == purpose,
                    VerificationOTP.consumed_at.is_(None)
                )
            )
        )

        otp_value = self.generate_otp()
        otp_hash = self._hash_otp(otp_value)
        
        if purpose == OTPPurpose.EMAIL_VERIFICATION:
            expiry_minutes = email_settings.EMAIL_OTP_EXPIRY_MINUTES
        else:
            expiry_minutes = email_settings.PASSWORD_RESET_OTP_EXPIRY_MINUTES

        otp_record = VerificationOTP(
            user_id=user_id,
            otp_hash=otp_hash,
            purpose=purpose,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=expiry_minutes)
        )
        db.add(otp_record)
        db.flush()
        return otp_value

    def verify_otp(self, db: Session, user_id: int, purpose: OTPPurpose, otp_value: str) -> None:
        otp_hash = self._hash_otp(otp_value)

        otp_record = db.query(VerificationOTP).filter(
            VerificationOTP.user_id == user_id,
            VerificationOTP.purpose == purpose,
            VerificationOTP.otp_hash == otp_hash,
            VerificationOTP.consumed_at.is_(None)
        ).first()

        if not otp_record:
            raise InvalidOTPError("Invalid OTP.")

        if otp_record.expires_at < datetime.now(timezone.utc):
            raise OTPExpiredError("OTP has expired.")

        # Mark consumed
        otp_record.consumed_at = datetime.now(timezone.utc)
        db.flush()
