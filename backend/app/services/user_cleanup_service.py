from datetime import datetime, timezone, timedelta
from typing import Tuple
from sqlalchemy.orm import Session # pyright: ignore[reportMissingImports]

from app.models.user import User
from app.models.verification_otp import VerificationOTP
from app.core.email_config import email_settings

class UserCleanupService:
    def cleanup_expired_unverified_users(self, db: Session) -> Tuple[int, int]:
        """
        Cleans up stale, unverified users and their associated OTPs in a single transaction.
        Exempts system accounts (demo users).
        
        Returns:
            Tuple[int, int]: (users_deleted, otps_deleted)
        """
        expiry_minutes = email_settings.ACCOUNT_VERIFICATION_EXPIRY_MINUTES
        expiry_threshold = datetime.now(timezone.utc) - timedelta(minutes=expiry_minutes)

        # Find expired, unverified, non-system accounts
        expired_users = db.query(User).filter(
            User.email_verified == False,
            User.is_system_account == False,
            User.created_at < expiry_threshold
        ).all()

        if not expired_users:
            return 0, 0

        expired_user_ids = [user.id for user in expired_users]

        try:
            # Delete associated OTPs first (maintaining referential integrity)
            otps_deleted = db.query(VerificationOTP).filter(
                VerificationOTP.user_id.in_(expired_user_ids)
            ).delete(synchronize_session=False)

            # Delete the users
            users_deleted = db.query(User).filter(
                User.id.in_(expired_user_ids)
            ).delete(synchronize_session=False)

            db.commit()
            return users_deleted, otps_deleted
        except Exception:
            db.rollback()
            raise
