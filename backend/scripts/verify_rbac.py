import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.user import User
from app.models.ticket import TicketPriority, TicketLevel
from app.schemas.ticket import TicketCreate
from app.services.ticket_service import TicketService
from app.exceptions.auth import InsufficientPermissionsError

def run_test_case(name: str, db, actor_email: str, ticket_level: TicketLevel, expect_success: bool):
    print(f"[{name}] {actor_email} attempting to escalate {ticket_level.value} ticket...")
    
    actor = db.query(User).filter_by(email=actor_email).first()
    if not actor:
        print(f"FAILED: User {actor_email} not found")
        return
        
    service = TicketService(db)
    
    # Create a dummy ticket from admin to test escalation
    admin = db.query(User).filter_by(email="admin@esp.local").first()
    ticket_data = TicketCreate(title="RBAC Test", description="Test", priority=TicketPriority.LOW)
    ticket = service.create(ticket_data, admin.id)
    
    # Hack the level to test specific boundary
    ticket.support_level = ticket_level
    db.commit()
    
    try:
        service.escalate(ticket.id, actor)
        if expect_success:
            print("  SUCCESS: Allowed as expected.")
        else:
            print("  FAILED: Was allowed but expected to be blocked!")
    except InsufficientPermissionsError:
        if not expect_success:
            print("  SUCCESS: Blocked as expected.")
        else:
            print("  FAILED: Was blocked but expected to be allowed!")

def verify():
    db = SessionLocal()
    try:
        run_test_case("L1 vs L1", db, "alice.l1@esp.local", TicketLevel.L1, True)
        run_test_case("L1 vs L2", db, "alice.l1@esp.local", TicketLevel.L2, False)
        
        run_test_case("L2 vs L1", db, "bob.l2@esp.local", TicketLevel.L1, True)
        run_test_case("L2 vs L2", db, "bob.l2@esp.local", TicketLevel.L2, True)
        run_test_case("L2 vs L3", db, "bob.l2@esp.local", TicketLevel.L3, False)
        
        run_test_case("L3 vs L1", db, "charlie.l3@esp.local", TicketLevel.L1, True)
        run_test_case("L3 vs L2", db, "charlie.l3@esp.local", TicketLevel.L2, True)
        run_test_case("L3 vs L3", db, "charlie.l3@esp.local", TicketLevel.L3, False)
        
        run_test_case("ADMIN vs L2", db, "admin@esp.local", TicketLevel.L2, True)
        
    finally:
        db.close()

if __name__ == "__main__":
    verify()
