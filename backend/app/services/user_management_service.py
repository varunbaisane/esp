from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.user import User
from app.models.role import Role
from app.repositories import UserRoleRepository
from app.schemas.user_management import UserSummaryResponse, RoleData
from app.core.roles import ROLE_HIERARCHY, get_role_rank
from app.services.user_state_service import UserStateService

class UserManagementService:
    def __init__(self, db: Session):
        self.db = db
        self.user_role_repo = UserRoleRepository(db)
        self.user_state_service = UserStateService(db)

    def _get_requester_rank(self, requester: User) -> int:
        roles = self.user_role_repo.list_roles_for_user(requester.id)
        return max((get_role_rank(r.name) for r in roles), default=0)

    def _get_assignable_roles(self, requester_rank: int) -> list[str]:
        assignable = []
        for role_name, rank in ROLE_HIERARCHY.items():
            if rank < requester_rank:
                assignable.append(role_name)
        return assignable

    def list_users(self, requester: User, search: str = None, status: str = None, role: str = None) -> list[UserSummaryResponse]:
        query = self.db.query(User)

        if search:
            search_pattern = f"%{search}%"
            query = query.filter(or_(
                User.full_name.ilike(search_pattern),
                User.email.ilike(search_pattern)
            ))
            
        users = query.all()
        requester_rank = self._get_requester_rank(requester)
        assignable_roles = self._get_assignable_roles(requester_rank)

        results = []
        for user in users:
            # We skip filtering at DB level for status/role for now to keep it simple,
            # and do it in-memory since we need to compute account_status anyway.
            # In a real enterprise system, we would join the tables.
            
            roles = self.user_role_repo.list_roles_for_user(user.id)
            current_role_obj = roles[0] if roles else None
            
            # Compute account status
            if not user.is_active:
                account_status = "DISABLED"
            elif self.user_state_service.is_pending_approval(user):
                account_status = "PENDING_APPROVAL"
            else:
                account_status = "ACTIVE"
                
            # Filter by computed status
            if status and status != "All" and status != account_status:
                continue
                
            # Filter by computed role
            if role and role != "All":
                if role == "Pending":
                    if account_status != "PENDING_APPROVAL":
                        continue
                elif not current_role_obj or current_role_obj.name != role:
                    continue
                    
            role_data = None
            target_rank = 0
            if current_role_obj:
                role_data = RoleData(code=current_role_obj.name, display_name=current_role_obj.name.replace("_", " ").title())
                target_rank = get_role_rank(current_role_obj.name)
            
            # If the requester doesn't outrank the target user, they can't modify them
            if requester_rank <= target_rank:
                user_assignable_roles = []
            else:
                user_assignable_roles = assignable_roles

            results.append(UserSummaryResponse(
                id=user.id,
                name=user.full_name,
                email=user.email,
                account_status=account_status,
                current_role=role_data,
                joined_at=user.created_at,
                last_login_at=None,
                assignable_roles=user_assignable_roles
            ))

        return results

    def get_user(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()
