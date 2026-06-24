import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session # pyrefly: ignore [missing-import]
from app.db.session import SessionLocal
from app.models.user import User
from app.models.ticket import TicketLevel
from app.services.ticket_service import TicketService
from app.schemas.ticket import TicketCreate
from app.exceptions.ticket import TicketAlreadyAssignedError
from app.exceptions.auth import InsufficientPermissionsError

def main():
    db: Session = SessionLocal()
    try:
        alice = db.query(User).filter(User.email == "alice.l1@esp.local").first()
        john = db.query(User).filter(User.email == "john.l1@esp.local").first()
        manager = db.query(User).filter(User.email == "manager@esp.local").first()
        
        service = TicketService(db)
        
        # 1. Create unassigned ticket
        print("Creating unassigned L1 ticket...")
        ticket = service.create(TicketCreate(title="Test", description="Test", priority="LOW"), alice.id)
        
        # 2. Claim by Alice
        print("Claiming ticket as Alice...")
        ticket = service.claim_ticket(ticket.id, alice)
        assert ticket.assigned_to_id == alice.id
        print("  ✅ Claim successful")
        
        # 3. Invalid claim by John
        print("John attempting to claim Alice's ticket...")
        try:
            service.claim_ticket(ticket.id, john)
            print("  ❌ Failed to prevent invalid claim")
            sys.exit(1)
        except TicketAlreadyAssignedError:
            print("  ✅ Blocked Invalid Claim (Race Condition)")
            
        # 4. Reassign by Manager
        print("Manager assigning ticket from Alice to John...")
        ticket = service.assign_ticket(ticket.id, john.id, manager)
        assert ticket.assigned_to_id == john.id
        print("  ✅ Reassign successful")
        
        # 5. Escalate nullifies owner
        print("John escalating ticket to L2...")
        ticket = service.escalate(ticket.id, john)
        assert ticket.assigned_to_id is None
        assert ticket.support_level == TicketLevel.L2
        print("  ✅ Escalate reset ownership")
        
        print("\nAll verifications passed! 🎉")
    finally:
        db.close()

if __name__ == "__main__":
    main()
