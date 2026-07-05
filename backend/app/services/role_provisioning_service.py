from sqlalchemy.orm import Session # pyrefly: ignore [missing-import]
from sqlalchemy import delete # pyrefly: ignore [missing-import]

from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.repositories import UserRoleRepository
from app.repositories.notification_repository import NotificationRepository
from app.services.notification_service import NotificationService
from app.core.roles import ROLE_HIERARCHY, get_role_rank

class RoleProvisioningService:
    def __init__(self, db: Session):
        self.db = db
        self.user_role_repo = UserRoleRepository(db)
        self._notification_service = NotificationService(NotificationRepository(db))

    def _get_requester_rank(self, requester: User) -> int:
        roles = self.user_role_repo.list_roles_for_user(requester.id)
        return max((get_role_rank(r.name) for r in roles), default=0)
        
    def _get_role_by_name(self, name: str) -> Role:
        role = self.db.query(Role).filter(Role.name == name).first()
        if not role:
            raise ValueError(f"Role {name} not found")
        return role

    def assign_role(self, target_user_id: int, role_code: str, current_user: User):
        if target_user_id == current_user.id:
            raise ValueError("Cannot modify your own roles")
            
        target_user = self.db.query(User).filter(User.id == target_user_id).first()
        if not target_user:
            raise ValueError("User not found")
            
        target_role_rank = get_role_rank(role_code)
        if target_role_rank == 0:
            raise ValueError(f"Invalid role code {role_code}")
            
        requester_rank = self._get_requester_rank(current_user)
        target_user_rank = self._get_requester_rank(target_user)
        
        # Rule: requester_rank > target_role_rank AND requester_rank > target_user_rank
        # This allows Admin (100) to assign Manager (90), L3 (30) etc.
        # It prevents Manager (90) from assigning Manager (90).
        # It prevents Manager (90) from assigning a lower role to another Manager (90).
        # It prevents Admin (100) from assigning Admin (100).
        if requester_rank <= target_role_rank:
            raise ValueError("You do not have permission to assign this role")
            
        if requester_rank <= target_user_rank:
            raise ValueError("You do not have permission to modify this user")
            
        # Check last admin guard before replacing roles
        self._check_last_admin_guard(target_user_id)

        current_roles = self.user_role_repo.list_roles_for_user(target_user_id)
        had_no_roles = len(current_roles) == 0

        # Replace existing engineering roles
        self.db.execute(
            delete(UserRole).where(UserRole.user_id == target_user_id)
        )
        
        # Assign new role
        role = self._get_role_by_name(role_code)
        new_assignment = UserRole(user_id=target_user_id, role_id=role.id)
        self.db.add(new_assignment)
        self.db.commit()
        
        if had_no_roles:
            self._notification_service.notify_first_role_assigned(target_user, role.name, current_user)
        else:
            self._notification_service.notify_role_assigned(target_user, role.name, current_user)
        
        # TODO: audit_logger.log(action="ASSIGN_ROLE", target=target_user_id, role=role_code, by=current_user.id)
        
    def remove_role(self, target_user_id: int, role_code: str, current_user: User):
        if target_user_id == current_user.id:
            raise ValueError("Cannot modify your own roles")
            
        target_user = self.db.query(User).filter(User.id == target_user_id).first()
        if not target_user:
            raise ValueError("User not found")
            
        target_role_rank = get_role_rank(role_code)
        if target_role_rank == 0:
            raise ValueError(f"Invalid role code {role_code}")
            
        requester_rank = self._get_requester_rank(current_user)
        target_user_rank = self._get_requester_rank(target_user)
        
        if requester_rank <= target_role_rank:
            raise ValueError("You do not have permission to remove this role")
            
        if requester_rank <= target_user_rank:
            raise ValueError("You do not have permission to modify this user")
            
        self._check_last_admin_guard(target_user_id, removing_role=role_code)
        
        role = self._get_role_by_name(role_code)
        
        assignment = self.db.query(UserRole).filter_by(user_id=target_user_id, role_id=role.id).first()
        if not assignment:
            raise ValueError("User does not have this role")
            
        self.db.delete(assignment)
        self.db.commit()

        self._notification_service.notify_role_removed(target_user, role.name, current_user)
        
        # TODO: audit_logger.log(action="REMOVE_ROLE", target=target_user_id, role=role_code, by=current_user.id)
        
    def _check_last_admin_guard(self, target_user_id: int, removing_role: str = None):
        """
        Ensures we never remove or replace the last ADMIN role in the system.
        Called during assignment (which drops all existing roles) and removal.
        """
        current_roles = self.user_role_repo.list_roles_for_user(target_user_id)
        has_admin = any(r.name == "ADMIN" for r in current_roles)
        
        if not has_admin:
            return
            
        # If removing a specific role and it's not ADMIN, it's fine.
        if removing_role and removing_role != "ADMIN":
            return
            
        # Target user is an ADMIN. We are either replacing all roles (assigning new)
        # or removing the ADMIN role explicitly. We must check if they are the LAST admin.
        admin_role = self._get_role_by_name("ADMIN")
        admin_count = self.db.query(UserRole).filter(UserRole.role_id == admin_role.id).count()
        
        if admin_count <= 1:
            raise ValueError("Cannot remove or replace the final Administrator in the system.")
