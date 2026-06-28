import os
import sys

# Add the backend root directory to Python path so 'app' can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.services.user_cleanup_service import UserCleanupService
from app.core.email_config import email_settings

def main():
    db = SessionLocal()
    try:
        cleanup_service = UserCleanupService()
        users_deleted, otps_deleted = cleanup_service.cleanup_expired_unverified_users(db)
        expiry = email_settings.ACCOUNT_VERIFICATION_EXPIRY_MINUTES

        print("========================================")
        print()
        print("Authentication Cleanup")
        print()
        print(f"Users Deleted : {users_deleted}")
        print()
        print(f"OTPs Deleted  : {otps_deleted}")
        print()
        print(f"Expiry        : {expiry} min")
        print()
        print("Completed")
        print()
        print("========================================")
    finally:
        db.close()

if __name__ == "__main__":
    main()
