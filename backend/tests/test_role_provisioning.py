import pytest
from app.services.role_provisioning_service import RoleProvisioningService
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.core.roles import ROLE_HIERARCHY

@pytest.fixture
def setup_roles(db):
    for role_name in ROLE_HIERARCHY.keys():
        db.add(Role(name=role_name))
    db.commit()

@pytest.fixture
def test_admin_user(db, setup_roles):
    admin = User(email="admin@example.com", full_name="Admin User", hashed_password="pw", is_active=True, email_verified=True)
    db.add(admin)
    db.commit()
    role = db.query(Role).filter_by(name="ADMIN").first()
    db.add(UserRole(user_id=admin.id, role_id=role.id))
    db.commit()
    return admin

@pytest.fixture
def test_manager_user(db, setup_roles):
    mgr = User(email="mgr@example.com", full_name="Manager User", hashed_password="pw", is_active=True, email_verified=True)
    db.add(mgr)
    db.commit()
    role = db.query(Role).filter_by(name="ENGINEERING_MANAGER").first()
    db.add(UserRole(user_id=mgr.id, role_id=role.id))
    db.commit()
    return mgr

@pytest.fixture
def test_pending_user(db, setup_roles):
    user = User(email="pending@example.com", full_name="Pending User", hashed_password="pw", is_active=True, email_verified=True)
    db.add(user)
    db.commit()
    return user

def test_admin_can_assign_manager(db, test_admin_user, test_pending_user):
    service = RoleProvisioningService(db)
    # Target is pending user, requester is admin (rank 100)
    service.assign_role(test_pending_user.id, "ENGINEERING_MANAGER", test_admin_user)
    
    # Check it worked
    roles = service.user_role_repo.list_roles_for_user(test_pending_user.id)
    assert len(roles) == 1
    assert roles[0].name == "ENGINEERING_MANAGER"

def test_manager_cannot_assign_manager(db, test_manager_user, test_pending_user):
    service = RoleProvisioningService(db)
    with pytest.raises(ValueError, match="You do not have permission"):
        service.assign_role(test_pending_user.id, "ENGINEERING_MANAGER", test_manager_user)

def test_manager_can_assign_support_roles(db, test_manager_user, test_pending_user):
    service = RoleProvisioningService(db)
    service.assign_role(test_pending_user.id, "SUPPORT_L1", test_manager_user)
    roles = service.user_role_repo.list_roles_for_user(test_pending_user.id)
    assert roles[0].name == "SUPPORT_L1"

def test_assign_role_replaces_previous(db, test_admin_user, test_manager_user):
    service = RoleProvisioningService(db)
    # Give manager an L1 role instead
    service.assign_role(test_manager_user.id, "SUPPORT_L1", test_admin_user)
    roles = service.user_role_repo.list_roles_for_user(test_manager_user.id)
    assert len(roles) == 1
    assert roles[0].name == "SUPPORT_L1"
    
    # Give them L2 role now
    service.assign_role(test_manager_user.id, "SUPPORT_L2", test_admin_user)
    roles = service.user_role_repo.list_roles_for_user(test_manager_user.id)
    assert len(roles) == 1
    assert roles[0].name == "SUPPORT_L2"

def test_self_modification_fails(db, test_admin_user):
    service = RoleProvisioningService(db)
    with pytest.raises(ValueError, match="Cannot modify your own roles"):
        service.assign_role(test_admin_user.id, "SUPPORT_L1", test_admin_user)

    with pytest.raises(ValueError, match="Cannot modify your own roles"):
        service.remove_role(test_admin_user.id, "ADMIN", test_admin_user)

def test_manager_cannot_modify_another_manager(db, test_manager_user, setup_roles):
    service = RoleProvisioningService(db)
    
    # Create a second manager
    mgr2 = User(email="mgr2@example.com", full_name="Manager Two", hashed_password="pw", is_active=True, email_verified=True)
    db.add(mgr2)
    db.commit()
    role = db.query(Role).filter_by(name="ENGINEERING_MANAGER").first()
    db.add(UserRole(user_id=mgr2.id, role_id=role.id))
    db.commit()

    # Manager 1 tries to assign a lower role (L1) to Manager 2
    with pytest.raises(ValueError, match="You do not have permission to modify this user"):
        service.assign_role(mgr2.id, "SUPPORT_L1", test_manager_user)
        
    # Manager 1 tries to remove Manager 2's role
    with pytest.raises(ValueError, match="You do not have permission to remove this role"):
        service.remove_role(mgr2.id, "ENGINEERING_MANAGER", test_manager_user)

def test_manager_cannot_modify_admin(db, test_manager_user, test_admin_user):
    service = RoleProvisioningService(db)
    with pytest.raises(ValueError, match="You do not have permission"):
        service.remove_role(test_admin_user.id, "ADMIN", test_manager_user)

def test_last_admin_guard(db, test_admin_user):
    service = RoleProvisioningService(db)
    # Try to make another admin modify the first admin.
    # We need a second admin to bypass self-modification check.
    second_admin = User(
        email="admin2@example.com",
        full_name="Admin Two",
        hashed_password="hashed_password",
        is_active=True,
        email_verified=True,
    )
    db.add(second_admin)
    db.commit()
    
    # Give second admin the ADMIN role so they can bypass requester_rank check
    admin_role = db.query(Role).filter_by(name="ADMIN").first()
    db.add(UserRole(user_id=second_admin.id, role_id=admin_role.id))
    db.commit()

    # Now we have 2 admins. Second admin can modify first admin if we mock rank.
    # By default Admin cannot modify Admin (rank 100 >= 100).
    dummy_requester = User(id=999) # Not saved
    service._get_requester_rank = lambda u: 102 if getattr(u, 'id', None) == 999 else (101 if getattr(u, 'id', None) == second_admin.id else 100)
    service.remove_role(test_admin_user.id, "ADMIN", second_admin)
    
    # Now there is only 1 admin (second_admin).
    with pytest.raises(ValueError, match="Cannot remove or replace the final Administrator"):
        service.remove_role(second_admin.id, "ADMIN", dummy_requester)
        
    with pytest.raises(ValueError, match="Cannot remove or replace the final Administrator"):
        # Let's say we have a third user trying to assign L1 to the last admin.
        service.assign_role(second_admin.id, "SUPPORT_L1", dummy_requester)
