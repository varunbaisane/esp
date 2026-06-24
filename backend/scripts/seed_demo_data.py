import os
import sys
from datetime import datetime, timezone, timedelta

# Add the backend root directory to Python path so 'app' can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session # pyrefly: ignore [missing-import]
from app.db.session import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.models.ticket import Ticket, TicketPriority, TicketStatus, TicketLevel
from app.domain.ticket_sla import calculate_sla_due
from app.core.security import hash_password

ROLES = [
    "ADMIN",
    "ENGINEERING_MANAGER",
    "SUPPORT_L1",
    "SUPPORT_L2",
    "SUPPORT_L3",
]

USERS = [
    {"email": "admin@esp.local", "full_name": "Admin User", "role": "ADMIN"},
    {"email": "manager@esp.local", "full_name": "Engineering Manager", "role": "ENGINEERING_MANAGER"},
    {"email": "alice.l1@esp.local", "full_name": "Alice Johnson", "role": "SUPPORT_L1"},
    {"email": "john.l1@esp.local", "full_name": "John Doe", "role": "SUPPORT_L1"},
    {"email": "sarah.l1@esp.local", "full_name": "Sarah Connor", "role": "SUPPORT_L1"},
    {"email": "bob.l2@esp.local", "full_name": "Bob Smith", "role": "SUPPORT_L2"},
    {"email": "mike.l2@esp.local", "full_name": "Mike Wazowski", "role": "SUPPORT_L2"},
    {"email": "charlie.l3@esp.local", "full_name": "Charlie Brown", "role": "SUPPORT_L3"},
    {"email": "david.l3@esp.local", "full_name": "David Wallace", "role": "SUPPORT_L3"},
    {"email": "test.user@esp.local", "full_name": "Test User", "role": None},
]

TICKETS = [
    {
        "title": "Database Connection Failure",
        "description": "The primary database is refusing connections from the backend service.",
        "status": TicketStatus.OPEN,
        "priority": TicketPriority.CRITICAL,
        "support_level": TicketLevel.L1,
        "creator": "test.user@esp.local",
    },
    {
        "title": "Frontend Login Redirect Loop",
        "description": "Users are complaining they get redirected back to the login page after authenticating.",
        "status": TicketStatus.IN_PROGRESS,
        "priority": TicketPriority.HIGH,
        "support_level": TicketLevel.L2,
        "creator": "alice.l1@esp.local",
        "assignee": "bob.l2@esp.local"
    },
    {
        "title": "Email Service Timeout",
        "description": "Notification emails are being delayed by up to 5 minutes.",
        "status": TicketStatus.OPEN,
        "priority": TicketPriority.MEDIUM,
        "support_level": TicketLevel.L1,
        "creator": "test.user@esp.local",
    },
    {
        "title": "Critical Production Outage",
        "description": "The entire ESP platform is down. 502 Bad Gateway errors on all endpoints.",
        "status": TicketStatus.IN_PROGRESS,
        "priority": TicketPriority.CRITICAL,
        "support_level": TicketLevel.L3,
        "creator": "manager@esp.local",
        "assignee": "charlie.l3@esp.local"
    }
]

def seed_data():
    db: Session = SessionLocal()
    try:
        print("Seeding Roles...")
        role_map = {}
        for role_name in ROLES:
            role = db.query(Role).filter(Role.name == role_name).first()
            if not role:
                role = Role(name=role_name)
                db.add(role)
                db.flush()
                print(f"  Created role: {role_name}")
            role_map[role_name] = role.id

        print("Seeding Users...")
        user_map = {}
        hashed_password = hash_password("Password123!")
        for u in USERS:
            user = db.query(User).filter(User.email == u["email"]).first()
            if not user:
                user = User(
                    email=u["email"],
                    full_name=u["full_name"],
                    hashed_password=hashed_password
                )
                db.add(user)
                db.flush()
                print(f"  Created user: {u['email']}")
            user_map[u["email"]] = user.id

            # Assign role
            if u["role"]:
                role = next((r for r in db.query(Role).all() if r.name == u["role"]), None)
                if role and role not in user.roles:
                    user.roles.append(role)
                    db.flush()
                    print(f"  Assigned {u['role']} to {u['email']}")

        print("Seeding Tickets...")
        # Check if we already have these demo tickets by checking titles
        for t in TICKETS:
            ticket = db.query(Ticket).filter(Ticket.title == t["title"]).first()
            if not ticket:
                now = datetime.now(timezone.utc)
                creator_id = user_map[t["creator"]]
                assignee_id = user_map[t["assignee"]] if t.get("assignee") else None
                
                # Randomize creation time slightly for demo purposes (e.g., 2 hours ago)
                created_at = now - timedelta(hours=2)
                
                ticket = Ticket(
                    title=t["title"],
                    description=t["description"],
                    status=t["status"],
                    priority=t["priority"],
                    support_level=t["support_level"],
                    created_by_id=creator_id,
                    assigned_to_id=assignee_id,
                    created_at=created_at,
                    sla_due_at=calculate_sla_due(t["priority"], created_at)
                )
                db.add(ticket)
                print(f"  Created ticket: {t['title']}")

        db.commit()
        print("Seed complete.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
