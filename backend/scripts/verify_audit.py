import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.user import User
from app.models.ticket import TicketPriority, TicketStatus
from app.schemas.ticket import TicketCreate, TicketUpdate
from app.services.ticket_service import TicketService
from app.repositories.audit_repository import AuditRepository
from app.domain import audit_actions

def verify():
    db = SessionLocal()
    try:
        service = TicketService(db)
        audit_repo = AuditRepository(db)

        # Get test user (admin)
        admin = db.query(User).filter_by(email="admin@esp.local").first()
        l1_user = db.query(User).filter_by(email="alice.l1@esp.local").first()
        
        if not admin or not l1_user:
            print("Demo users missing. Run seed script first.")
            return

        print("1. Creating ticket...")
        ticket_data = TicketCreate(title="Audit Test Ticket", description="Test", priority=TicketPriority.LOW)
        ticket = service.create(ticket_data, admin.id)

        print("2. Assigning ticket...")
        update_data = TicketUpdate(assigned_to_id=l1_user.id)
        service.update(ticket.id, update_data, admin.id)

        print("3. Escalating ticket...")
        service.escalate(ticket.id, l1_user.id)

        print("4. Changing status to IN_PROGRESS...")
        update_data = TicketUpdate(status=TicketStatus.IN_PROGRESS)
        service.update(ticket.id, update_data, l1_user.id)

        print("5. Resolving ticket...")
        update_data = TicketUpdate(status=TicketStatus.RESOLVED)
        service.update(ticket.id, update_data, l1_user.id)

        print("6. Closing ticket...")
        update_data = TicketUpdate(status=TicketStatus.CLOSED)
        service.update(ticket.id, update_data, admin.id)

        print("Fetching audit logs for ticket...")
        logs = audit_repo.list_for_ticket(ticket.id)
        
        # Reverse to get chronological order
        logs.reverse()

        expected_actions = [
            audit_actions.TICKET_CREATED,
            audit_actions.TICKET_ASSIGNED,
            audit_actions.TICKET_ESCALATED,
            audit_actions.STATUS_CHANGED,
            audit_actions.TICKET_RESOLVED,
            audit_actions.TICKET_CLOSED
        ]

        if len(logs) != 6:
            print(f"FAILED: Expected 6 logs, got {len(logs)}")
            for log in logs:
                print(f" - {log.action}")
            return

        for i, (log, expected) in enumerate(zip(logs, expected_actions)):
            if log.action != expected:
                print(f"FAILED: Step {i+1} expected {expected}, got {log.action}")
                return
            
            if i > 0:
                if log.created_at < logs[i-1].created_at:
                    print(f"FAILED: created_at is not strictly increasing at index {i}")
                    return

        print("\nSUCCESS! Audit sequence verified:")
        for log in logs:
            print(f"[{log.created_at.strftime('%H:%M:%S.%f')}] {log.actor_name}: {log.action}")
            if log.event_metadata:
                print(f"   Metadata: {log.event_metadata}")

    finally:
        db.close()

if __name__ == "__main__":
    verify()
