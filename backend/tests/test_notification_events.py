import pytest # pyrefly: ignore [missing-import]
from app.services.ticket_service import TicketService
from app.services.role_provisioning_service import RoleProvisioningService
from app.models.user import User
from app.models.role import Role
from app.models.ticket import TicketPriority, TicketStatus
from app.models.notification import Notification
from app.schemas.ticket import TicketCreate, TicketUpdate
from app.core.notifications import NotificationType

def test_ticket_assigned_and_reassigned(db):
    ticket_service = TicketService(db)
    
    admin = User(email="admin@test.com", full_name="Admin", hashed_password="pw", is_system_account=True)
    admin_role = Role(name="ADMIN")
    admin.roles.append(admin_role)
    
    l1_role = Role(name="SUPPORT_L1")
    
    user1 = User(email="user1@test.com", full_name="User 1", hashed_password="pw")
    user1.roles.append(l1_role)
    
    user2 = User(email="user2@test.com", full_name="User 2", hashed_password="pw")
    user2.roles.append(l1_role)
    
    db.add_all([admin, admin_role, user1, user2, l1_role])
    db.commit()

    # Create ticket
    ticket = ticket_service.create(
        TicketCreate(title="Test Ticket", description="Desc", priority=TicketPriority.MEDIUM),
        user_id=user1.id
    )
    db.commit()

    # 1. Claim ticket (Self-assignment)
    # Actor == Recipient -> No notification should be generated
    ticket_service.claim_ticket(ticket.id, admin)
    
    notifs = db.query(Notification).all()
    assert len(notifs) == 0

    # 2. Reassign ticket (Admin assigns to user1)
    ticket_service.assign_ticket(ticket.id, assignee_id=user1.id, actor=admin)
    
    notifs = db.query(Notification).filter_by(type=NotificationType.TICKET_REASSIGNED).all()
    assert len(notifs) == 1
    assert notifs[0].recipient_id == user1.id
    assert notifs[0].actor_id == admin.id
    
def test_ticket_status_priority_unassigned(db):
    ticket_service = TicketService(db)
    
    admin = User(email="admin@test.com", full_name="Admin", hashed_password="pw", is_system_account=True)
    admin_role = Role(name="ADMIN")
    admin.roles.append(admin_role)
    
    db.add_all([admin, admin_role])
    db.commit()

    ticket = ticket_service.create(
        TicketCreate(title="Test Ticket", description="Desc", priority=TicketPriority.MEDIUM),
        user_id=admin.id
    )

    # Status change on unassigned ticket -> no notification
    ticket_service.update(ticket.id, TicketUpdate(status=TicketStatus.IN_PROGRESS), admin)
    # Priority change on unassigned ticket -> no notification
    ticket_service.update(ticket.id, TicketUpdate(priority=TicketPriority.HIGH), admin)
    
    notifs = db.query(Notification).all()
    assert len(notifs) == 0

def test_ticket_status_priority_assigned(db):
    ticket_service = TicketService(db)
    
    admin = User(email="admin@test.com", full_name="Admin", hashed_password="pw", is_system_account=True)
    admin_role = Role(name="ADMIN")
    admin.roles.append(admin_role)
    
    user1 = User(email="user1@test.com", full_name="User 1", hashed_password="pw")
    l1_role = Role(name="SUPPORT_L1")
    user1.roles.append(l1_role)
    
    db.add_all([admin, admin_role, user1, l1_role])
    db.commit()

    ticket = ticket_service.create(
        TicketCreate(title="Test Ticket", description="Desc", priority=TicketPriority.MEDIUM),
        user_id=admin.id
    )
    
    ticket_service.assign_ticket(ticket.id, assignee_id=user1.id, actor=admin)
    
    # 1. Status change
    ticket_service.update(ticket.id, TicketUpdate(status=TicketStatus.IN_PROGRESS), admin)
    
    notifs = db.query(Notification).filter_by(type=NotificationType.TICKET_STATUS_CHANGED).all()
    assert len(notifs) == 1
    assert notifs[0].recipient_id == user1.id

    # 2. Priority change
    ticket_service.update(ticket.id, TicketUpdate(priority=TicketPriority.HIGH), admin)
    notifs = db.query(Notification).filter_by(type=NotificationType.TICKET_PRIORITY_CHANGED).all()
    assert len(notifs) == 1
    assert notifs[0].recipient_id == user1.id

def test_role_provisioning_onboard_and_assign(db):
    role_service = RoleProvisioningService(db)
    
    admin = User(email="admin@test.com", full_name="Admin", hashed_password="pw", is_system_account=True)
    admin_role = Role(name="ADMIN")
    admin.roles.append(admin_role)
    
    l1_role = Role(name="SUPPORT_L1")
    l2_role = Role(name="SUPPORT_L2")
    
    user1 = User(email="user1@test.com", full_name="User 1", hashed_password="pw")
    
    db.add_all([admin, admin_role, l1_role, l2_role, user1])
    db.commit()

    # 1. First time role assignment -> Onboarding
    role_service.assign_role(user1.id, "SUPPORT_L1", admin)
    
    notifs = db.query(Notification).filter_by(type=NotificationType.ROLE_ASSIGNED).all()
    assert len(notifs) == 1
    assert "Welcome" in notifs[0].title
    assert notifs[0].recipient_id == user1.id

    # 2. Subsequent role assignment -> Standard Role Assigned
    role_service.assign_role(user1.id, "SUPPORT_L2", admin)
    
    notifs = db.query(Notification).filter_by(type=NotificationType.ROLE_ASSIGNED).all()
    assert len(notifs) == 2
    assert "Role Assigned" in notifs[1].title

    # 3. Role removal -> Role Removed
    role_service.remove_role(user1.id, "SUPPORT_L2", admin)
    notifs = db.query(Notification).filter_by(type=NotificationType.ROLE_REMOVED).all()
    assert len(notifs) == 1
    assert notifs[0].recipient_id == user1.id

def test_notification_negative_scenarios(db):
    ticket_service = TicketService(db)
    
    admin = User(email="admin@test.com", full_name="Admin", hashed_password="pw", is_system_account=True)
    admin_role = Role(name="ADMIN")
    admin.roles.append(admin_role)
    
    user1 = User(email="user1@test.com", full_name="User 1", hashed_password="pw")
    l1_role = Role(name="SUPPORT_L1")
    user1.roles.append(l1_role)
    
    db.add_all([admin, admin_role, user1, l1_role])
    db.commit()

    ticket = ticket_service.create(
        TicketCreate(title="Test Ticket", description="Desc", priority=TicketPriority.MEDIUM),
        user_id=admin.id
    )

    initial_notifs_count = db.query(Notification).count()

    # Priority changes on an unassigned ticket -> NO notification
    ticket_service.update(ticket.id, TicketUpdate(priority=TicketPriority.HIGH), admin)
    assert db.query(Notification).count() == initial_notifs_count
    
    # Status changes on an unassigned ticket -> NO notification
    ticket_service.update(ticket.id, TicketUpdate(status=TicketStatus.IN_PROGRESS), admin)
    assert db.query(Notification).count() == initial_notifs_count

    # Actor == Recipient (Self assignment via claim) -> NO notification
    ticket_service.claim_ticket(ticket.id, admin)
    assert db.query(Notification).count() == initial_notifs_count

    # Assignment remains the same -> NO notification
    ticket_service.assign_ticket(ticket.id, assignee_id=admin.id, actor=admin)
    assert db.query(Notification).count() == initial_notifs_count
