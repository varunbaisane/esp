from sqlalchemy import select, func  # pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session  # pyrefly: ignore [missing-import]

from app.models.ticket import Ticket, TicketStatus


class TicketRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, ticket: Ticket) -> Ticket:
        self._session.add(ticket)
        self._session.flush()
        self._session.refresh(ticket)
        return ticket

    def get_by_id(self, ticket_id: int) -> Ticket | None:
        stmt = select(Ticket).where(Ticket.id == ticket_id)
        return self._session.execute(stmt).scalar_one_or_none()

    def list(self) -> list[Ticket]:
        stmt = select(Ticket).order_by(Ticket.id.desc())
        return list(self._session.execute(stmt).scalars().all())

    def list_filtered(
        self,
        status: TicketStatus | None = None,
        priority: str | None = None,
        support_level: str | None = None,
        assigned_to_id: int | None = None,
        sla_status: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        limit: int = 25,
        offset: int = 0
    ) -> tuple[list[Ticket], int]:
        from datetime import datetime, timezone
        from sqlalchemy import case, func, desc, asc
        from app.schemas.ticket import SLAStatus
        from app.models.ticket import TicketPriority, TicketLevel
        
        stmt = select(Ticket)
        
        # Filters
        if status:
            if status == "ACTIVE":
                stmt = stmt.where(Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS]))
            else:
                stmt = stmt.where(Ticket.status == status)
        if priority:
            stmt = stmt.where(Ticket.priority == TicketPriority(priority))
        if support_level:
            stmt = stmt.where(Ticket.support_level == TicketLevel(support_level))
        if assigned_to_id is not None:
            if assigned_to_id == -1:
                stmt = stmt.where(Ticket.assigned_to_id.is_(None))
            elif assigned_to_id == -2:
                stmt = stmt.where(Ticket.assigned_to_id.is_not(None))
            else:
                stmt = stmt.where(Ticket.assigned_to_id == assigned_to_id)
                
        now = datetime.now(timezone.utc)
        if sla_status:
            if sla_status == SLAStatus.BREACHED:
                stmt = stmt.where(Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS]))
                stmt = stmt.where(Ticket.sla_due_at < now)
            elif sla_status == SLAStatus.AT_RISK:
                stmt = stmt.where(Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS]))
                stmt = stmt.where(Ticket.sla_due_at >= now)
                stmt = stmt.where(
                    (func.extract('epoch', Ticket.sla_due_at) - now.timestamp()) <= 
                    (func.extract('epoch', Ticket.sla_due_at) - func.extract('epoch', Ticket.created_at)) * 0.25
                )
            elif sla_status == SLAStatus.HEALTHY:
                # Either resolved/closed, or open and > 25% time left
                stmt = stmt.where(
                    Ticket.status.in_([TicketStatus.RESOLVED, TicketStatus.CLOSED]) |
                    (
                        (Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS])) &
                        (Ticket.sla_due_at >= now) &
                        ((func.extract('epoch', Ticket.sla_due_at) - now.timestamp()) > 
                        (func.extract('epoch', Ticket.sla_due_at) - func.extract('epoch', Ticket.created_at)) * 0.25)
                    )
                )

        # Sorting
        order_func = desc if sort_order.lower() == "desc" else asc
        
        if sort_by == "priority":
            # Enum sorting (Critical > High > Medium > Low)
            # This requires a CASE statement for custom ranking
            priority_rank = case(
                (Ticket.priority == TicketPriority.CRITICAL, 4),
                (Ticket.priority == TicketPriority.HIGH, 3),
                (Ticket.priority == TicketPriority.MEDIUM, 2),
                (Ticket.priority == TicketPriority.LOW, 1),
                else_=0
            )
            stmt = stmt.order_by(order_func(priority_rank), order_func(Ticket.created_at))
        elif sort_by == "level":
            level_rank = case(
                (Ticket.support_level == TicketLevel.L3, 3),
                (Ticket.support_level == TicketLevel.L2, 2),
                (Ticket.support_level == TicketLevel.L1, 1),
                else_=0
            )
            stmt = stmt.order_by(order_func(level_rank), order_func(Ticket.created_at))
        elif sort_by == "sla_status":
            # BREACHED (3), AT_RISK (2), HEALTHY (1)
            # HEALTHY includes resolved/closed or plenty of time.
            breached_cond = (Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS])) & (Ticket.sla_due_at < now)
            at_risk_cond = (Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS])) & (Ticket.sla_due_at >= now) & (
                (func.extract('epoch', Ticket.sla_due_at) - now.timestamp()) <= 
                (func.extract('epoch', Ticket.sla_due_at) - func.extract('epoch', Ticket.created_at)) * 0.25
            )
            
            sla_rank = case(
                (breached_cond, 3),
                (at_risk_cond, 2),
                else_=1
            )
            stmt = stmt.order_by(order_func(sla_rank), order_func(Ticket.sla_due_at))
        elif sort_by == "sla_due_at":
            stmt = stmt.order_by(order_func(Ticket.sla_due_at), order_func(Ticket.created_at))
        elif sort_by == "updated_at":
            stmt = stmt.order_by(order_func(Ticket.updated_at), order_func(Ticket.created_at))
        else:
            stmt = stmt.order_by(order_func(Ticket.created_at))

        # Total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self._session.execute(count_stmt).scalar() or 0

        # Pagination
        stmt = stmt.limit(limit).offset(offset)
        items = list(self._session.execute(stmt).scalars().all())

        return items, total

    def list_by_creator(self, user_id: int) -> list[Ticket]:
        stmt = select(Ticket).where(Ticket.created_by_id == user_id).order_by(Ticket.id.desc())
        return list(self._session.execute(stmt).scalars().all())

    def list_by_status(self, status: TicketStatus) -> list[Ticket]:
        stmt = select(Ticket).where(Ticket.status == status).order_by(Ticket.id.desc())
        return list(self._session.execute(stmt).scalars().all())

    def list_by_assignee(self, user_id: int) -> list[Ticket]:
        stmt = select(Ticket).where(Ticket.assigned_to_id == user_id).order_by(Ticket.id.desc())
        return list(self._session.execute(stmt).scalars().all())

    def get_stats(self, user_id: int) -> dict[str, int]:
        from datetime import datetime, timezone
        from app.models.ticket import TicketPriority
        
        now = datetime.now(timezone.utc)
        
        open_count = self._session.execute(
            select(func.count(Ticket.id))
            .where(Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS]))
        ).scalar() or 0
        
        breached_count = self._session.execute(
            select(func.count(Ticket.id))
            .where(Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS]))
            .where(Ticket.sla_due_at < now)
        ).scalar() or 0
        
        high_count = self._session.execute(
            select(func.count(Ticket.id))
            .where(Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS]))
            .where(Ticket.priority == TicketPriority.HIGH)
        ).scalar() or 0
        
        critical_count = self._session.execute(
            select(func.count(Ticket.id))
            .where(Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS]))
            .where(Ticket.priority == TicketPriority.CRITICAL)
        ).scalar() or 0

        my_assigned_count = self._session.execute(
            select(func.count(Ticket.id))
            .where(Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS]))
            .where(Ticket.assigned_to_id == user_id)
        ).scalar() or 0

        unassigned_count = self._session.execute(
            select(func.count(Ticket.id))
            .where(Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS]))
            .where(Ticket.assigned_to_id.is_(None))
        ).scalar() or 0

        return {
            "open_tickets": open_count,
            "breached_tickets": breached_count,
            "high_priority_tickets": high_count,
            "critical_tickets": critical_count,
            "my_assigned_tickets": my_assigned_count,
            "unassigned_tickets": unassigned_count,
        }

    def get_user_ticket_stats(self, user_id: int) -> dict[str, int]:
        from datetime import datetime, timezone
        from app.models.ticket import TicketPriority
        
        now = datetime.now(timezone.utc)
        
        assigned_count = self._session.execute(
            select(func.count(Ticket.id))
            .where(Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS]))
            .where(Ticket.assigned_to_id == user_id)
        ).scalar() or 0

        breached_count = self._session.execute(
            select(func.count(Ticket.id))
            .where(Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS]))
            .where(Ticket.assigned_to_id == user_id)
            .where(Ticket.sla_due_at < now)
        ).scalar() or 0

        high_count = self._session.execute(
            select(func.count(Ticket.id))
            .where(Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS]))
            .where(Ticket.assigned_to_id == user_id)
            .where(Ticket.priority == TicketPriority.HIGH)
        ).scalar() or 0

        critical_count = self._session.execute(
            select(func.count(Ticket.id))
            .where(Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS]))
            .where(Ticket.assigned_to_id == user_id)
            .where(Ticket.priority == TicketPriority.CRITICAL)
        ).scalar() or 0

        return {
            "assigned_tickets": assigned_count,
            "critical_tickets": critical_count,
            "high_priority_tickets": high_count,
            "breached_tickets": breached_count,
        }

    def get_team_operations_stats(self) -> dict[str, int]:
        from datetime import datetime, timezone
        from app.models.ticket import TicketLevel
        
        now = datetime.now(timezone.utc)
        active_statuses = [TicketStatus.OPEN, TicketStatus.IN_PROGRESS]
        
        def count_for_level(level: TicketLevel):
            active = self._session.execute(
                select(func.count(Ticket.id))
                .where(Ticket.status.in_(active_statuses))
                .where(Ticket.support_level == level)
            ).scalar() or 0
            
            unassigned = self._session.execute(
                select(func.count(Ticket.id))
                .where(Ticket.status.in_(active_statuses))
                .where(Ticket.support_level == level)
                .where(Ticket.assigned_to_id.is_(None))
            ).scalar() or 0
            
            breached = self._session.execute(
                select(func.count(Ticket.id))
                .where(Ticket.status.in_(active_statuses))
                .where(Ticket.support_level == level)
                .where(Ticket.sla_due_at < now)
            ).scalar() or 0
            
            return active, unassigned, breached

        l1_active, l1_unassigned, l1_breached = count_for_level(TicketLevel.L1)
        l2_active, l2_unassigned, l2_breached = count_for_level(TicketLevel.L2)
        l3_active, l3_unassigned, l3_breached = count_for_level(TicketLevel.L3)

        return {
            "l1_active": l1_active,
            "l2_active": l2_active,
            "l3_active": l3_active,
            "l1_unassigned": l1_unassigned,
            "l2_unassigned": l2_unassigned,
            "l3_unassigned": l3_unassigned,
            "l1_breached": l1_breached,
            "l2_breached": l2_breached,
            "l3_breached": l3_breached,
        }

    def get_engineer_workloads(self) -> list[dict]:
        from app.models.user import User
        from app.models.user_role import user_roles
        from app.models.role import Role
        
        support_users = self._session.execute(
            select(User.id, User.full_name, Role.name)
            .join(user_roles, User.id == user_roles.c.user_id)
            .join(Role, user_roles.c.role_id == Role.id)
            .where(Role.name.like("SUPPORT_%"))
        ).all()
        
        workloads = []
        for user_id, full_name, role_name in support_users:
            stats = self.get_user_ticket_stats(user_id)
            workloads.append({
                "user_id": user_id,
                "full_name": full_name,
                "role": role_name,
                "assigned_tickets": stats["assigned_tickets"],
                "critical_tickets": stats["critical_tickets"],
                "breached_tickets": stats["breached_tickets"],
            })
            
        return workloads
