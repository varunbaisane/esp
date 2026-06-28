import pytest # pyrefly: ignore [missing-import]
import sys
import os

from sqlalchemy.orm import Session # pyrefly: ignore [missing-import]
from app.models.user import User

def test_seed_demo_data(db: Session):
    # Import the seed script
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))
    import seed_demo_data # pyrefly: ignore [missing-import]
    
    # Run the seeder
    seed_demo_data.seed_data(db)
    
    # Verify the users were seeded properly
    users = db.query(User).all()
    
    assert len(users) > 0
    assert any(u.is_system_account for u in users)
    assert all(u.email_verified for u in users if u.is_system_account)
    assert all(u.email_verified_at is not None for u in users if u.is_system_account)
