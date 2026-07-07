import os
import sys
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Setup minimal test DB environment
os.environ["DATABASE_URL"] = "postgresql+psycopg://esp:esp_test_password@localhost:5433/esp_test_db"
os.environ["EMAIL_PROVIDER"] = "console"
os.environ["SECRET_KEY"] = "testsecret"

from app.db.base import Base
from app.models.user import User
from app.models.ticket import Ticket
from app.models.notification_preference import NotificationPreference, NotificationType, NotificationChannel
from app.schemas.ticket import TicketCreate
from app.services.ticket_service import TicketService
from app.services.notification_preference_service import NotificationPreferenceService

engine = create_engine(os.environ["DATABASE_URL"])
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def reset_db(db):
    for table in reversed(Base.metadata.sorted_tables):
        db.execute(table.delete())
    db.commit()

def run_verification():
    print("--- STARTING END-TO-END NOTIFICATION VERIFICATION ---")
    db = SessionLocal()
    reset_db(db)

    try:
        # Create users
        user = User(
            email="test_recipient@example.com",
            full_name="Test Recipient",
            hashed_password="hash",
            email_verified=True
        )
        db.add(user)
        
        actor = User(
            email="test_actor@example.com",
            full_name="Test Actor",
            hashed_password="hash",
            email_verified=True
        )
        db.add(actor)
        db.commit()
        db.refresh(user)
        db.refresh(actor)

        user_id = user.id
        actor_id = actor.id

        # Generate preferences
        pref_service = NotificationPreferenceService(db)
        pref_service.create_defaults(user_id)
        
        print("\n[STEP 1] Enable EMAIL for Ticket Assigned")
        # Ensure it's enabled
        prefs = pref_service.get_preferences(user_id)
        target_pref = next(p for p in prefs if p.notification_type == NotificationType.TICKET_ASSIGNED.value and p.channel == NotificationChannel.EMAIL.value)
        pref_service.update_preference(user_id, target_pref.id, True)

        print("\n[STEP 2] Assigning ticket...")
        ticket_service = TicketService(db)
        
        # We need another user as assignee
        ticket_service.create(TicketCreate(title="Test Ticket", description="Desc", priority="LOW"), actor_id)
        ticket = db.query(Ticket).first()
        ticket.assigned_to_id = user.id
        db.commit()

        # Manually trigger assignment notification since TicketService might only do creation notifications
        from app.services.notification_service import NotificationService
        from app.repositories.notification_repository import NotificationRepository
        from app.services.notification_delivery_dispatcher import NotificationDeliveryDispatcher
        from app.services.email_service import EmailService
        from app.email.factory import get_email_provider

        email_provider = get_email_provider()
        
        # Spy on the send method
        original_send = email_provider.send
        emails_sent = []
        def mock_send(msg):
            emails_sent.append(msg)
            original_send(msg)
        email_provider.send = mock_send

        email_service = EmailService(email_provider)
        dispatcher = NotificationDeliveryDispatcher(email_service, pref_service)
        notification_service = NotificationService(NotificationRepository(db), dispatcher)

        # Trigger notification
        notification_service.notify_ticket_assigned(ticket=ticket, actor=actor, assignee_id=user.id)

        print("\nExpected: Database notification exists.")
        from app.models.notification import Notification
        notif = db.query(Notification).first()
        print(f"Result: {'YES' if notif else 'NO'}")

        print("Expected: Notification email received.")
        print(f"Result: {'YES' if len(emails_sent) == 1 else 'NO'} (Emails sent: {len(emails_sent)})")
        if emails_sent:
            print(f"Email To: {emails_sent[0].to}, Subject: {emails_sent[0].subject}")

        # Now Disable EMAIL
        print("\n[STEP 3] Disable EMAIL for Ticket Assigned")
        pref_service.update_preference(user.id, target_pref.id, False)

        print("\n[STEP 4] Assigning another ticket...")
        emails_sent.clear()
        ticket_2_model = ticket_service.create(TicketCreate(title="Test 2", description="Desc 2", priority="LOW"), actor.id)
        ticket_2 = db.query(Ticket).get(ticket_2_model.id)
        ticket_2.assigned_to_id = user.id
        db.commit()

        notification_service.notify_ticket_assigned(ticket=ticket_2, actor=actor, assignee_id=user.id)

        print("\nExpected: Database notification exists (second one).")
        notifs = db.query(Notification).all()
        print(f"Result: {'YES' if len(notifs) == 2 else 'NO'} (Count: {len(notifs)})")

        print("Expected: No email received.")
        print(f"Result: {'YES' if len(emails_sent) == 0 else 'NO'} (Emails sent: {len(emails_sent)})")
        if emails_sent:
            print(f"Email To: {emails_sent[0].to}, Subject: {emails_sent[0].subject}")

    finally:
        db.close()

if __name__ == "__main__":
    run_verification()
