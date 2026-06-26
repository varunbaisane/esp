from sqlalchemy import select, func  # pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session, selectinload  # pyrefly: ignore [missing-import]

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
        stmt = select(Ticket).where(Ticket.id == ticket_id).options(selectinload(Ticket.creator), selectinload(Ticket.assigned_to))
        return self._session.execute(stmt).scalar_one_or_none()

    def list(self) -> list[Ticket]:
        stmt = select(Ticket).order_by(Ticket.id.desc()).options(selectinload(Ticket.creator), selectinload(Ticket.assigned_to))
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
        stmt = stmt.options(selectinload(Ticket.creator), selectinload(Ticket.assigned_to))
        stmt = stmt.limit(limit).offset(offset)
        items = list(self._session.execute(stmt).scalars().all())

        return items, total

    def list_by_creator(self, user_id: int) -> list[Ticket]:
        stmt = select(Ticket).where(Ticket.created_by_id == user_id).order_by(Ticket.id.desc()).options(selectinload(Ticket.creator), selectinload(Ticket.assigned_to))
        return list(self._session.execute(stmt).scalars().all())

    def list_by_status(self, status: TicketStatus) -> list[Ticket]:
        stmt = select(Ticket).where(Ticket.status == status).order_by(Ticket.id.desc()).options(selectinload(Ticket.creator), selectinload(Ticket.assigned_to))
        return list(self._session.execute(stmt).scalars().all())

    def list_by_assignee(self, user_id: int) -> list[Ticket]:
        stmt = select(Ticket).where(Ticket.assigned_to_id == user_id).order_by(Ticket.id.desc()).options(selectinload(Ticket.creator), selectinload(Ticket.assigned_to))
        return list(self._session.execute(stmt).scalars().all())

    def get_stats(self, user_id: int) -> dict[str, int]:
        from datetime import datetime, timezone
        from sqlalchemy import case, func
        from app.models.ticket import TicketPriority
        
        now = datetime.now(timezone.utc)
        active_statuses = [TicketStatus.OPEN, TicketStatus.IN_PROGRESS]
        
        stmt = select(
            func.sum(case((Ticket.status.in_(active_statuses), 1), else_=0)).label("open_tickets"),
            func.sum(case((Ticket.status.in_(active_statuses) & (Ticket.sla_due_at < now), 1), else_=0)).label("breached_tickets"),
            func.sum(case((Ticket.status.in_(active_statuses) & (Ticket.priority == TicketPriority.HIGH), 1), else_=0)).label("high_count"),
            func.sum(case((Ticket.status.in_(active_statuses) & (Ticket.priority == TicketPriority.CRITICAL), 1), else_=0)).label("critical_count"),
            func.sum(case((Ticket.status.in_(active_statuses) & (Ticket.assigned_to_id == user_id), 1), else_=0)).label("my_assigned"),
            func.sum(case((Ticket.status.in_(active_statuses) & (Ticket.assigned_to_id.is_(None)), 1), else_=0)).label("unassigned_count"),
        )
        
        result = self._session.execute(stmt).first()
        
        return {
            "open_tickets": int(getattr(result, 'open_tickets', 0) or 0),
            "breached_tickets": int(getattr(result, 'breached_tickets', 0) or 0),
            "high_priority_tickets": int(getattr(result, 'high_count', 0) or 0),
            "critical_tickets": int(getattr(result, 'critical_count', 0) or 0),
            "my_assigned_tickets": int(getattr(result, 'my_assigned', 0) or 0),
            "unassigned_tickets": int(getattr(result, 'unassigned_count', 0) or 0),
        }

    def get_user_ticket_stats(self, user_id: int) -> dict[str, int]:
        from datetime import datetime, timezone
        from sqlalchemy import case, func
        from app.models.ticket import TicketPriority
        
        now = datetime.now(timezone.utc)
        active_statuses = [TicketStatus.OPEN, TicketStatus.IN_PROGRESS]
        
        stmt = select(
            func.sum(case((Ticket.status.in_(active_statuses) & (Ticket.assigned_to_id == user_id), 1), else_=0)).label("assigned"),
            func.sum(case((Ticket.status.in_(active_statuses) & (Ticket.assigned_to_id == user_id) & (Ticket.sla_due_at < now), 1), else_=0)).label("breached"),
            func.sum(case((Ticket.status.in_(active_statuses) & (Ticket.assigned_to_id == user_id) & (Ticket.priority == TicketPriority.HIGH), 1), else_=0)).label("high"),
            func.sum(case((Ticket.status.in_(active_statuses) & (Ticket.assigned_to_id == user_id) & (Ticket.priority == TicketPriority.CRITICAL), 1), else_=0)).label("critical"),
        )
        
        result = self._session.execute(stmt).first()

        return {
            "assigned_tickets": int(getattr(result, 'assigned', 0) or 0),
            "critical_tickets": int(getattr(result, 'critical', 0) or 0),
            "high_priority_tickets": int(getattr(result, 'high', 0) or 0),
            "breached_tickets": int(getattr(result, 'breached', 0) or 0),
        }

    def get_team_operations_stats(self) -> dict[str, int]:
        from datetime import datetime, timezone
        from sqlalchemy import case, func
        from app.models.ticket import TicketLevel
        
        now = datetime.now(timezone.utc)
        active_statuses = [TicketStatus.OPEN, TicketStatus.IN_PROGRESS]
        
        stmt = select(
            func.sum(case((Ticket.status.in_(active_statuses) & (Ticket.support_level == TicketLevel.L1), 1), else_=0)).label("l1_active"),
            func.sum(case((Ticket.status.in_(active_statuses) & (Ticket.support_level == TicketLevel.L2), 1), else_=0)).label("l2_active"),
            func.sum(case((Ticket.status.in_(active_statuses) & (Ticket.support_level == TicketLevel.L3), 1), else_=0)).label("l3_active"),
            
            func.sum(case((Ticket.status.in_(active_statuses) & (Ticket.support_level == TicketLevel.L1) & (Ticket.assigned_to_id.is_(None)), 1), else_=0)).label("l1_unassigned"),
            func.sum(case((Ticket.status.in_(active_statuses) & (Ticket.support_level == TicketLevel.L2) & (Ticket.assigned_to_id.is_(None)), 1), else_=0)).label("l2_unassigned"),
            func.sum(case((Ticket.status.in_(active_statuses) & (Ticket.support_level == TicketLevel.L3) & (Ticket.assigned_to_id.is_(None)), 1), else_=0)).label("l3_unassigned"),
            
            func.sum(case((Ticket.status.in_(active_statuses) & (Ticket.support_level == TicketLevel.L1) & (Ticket.sla_due_at < now), 1), else_=0)).label("l1_breached"),
            func.sum(case((Ticket.status.in_(active_statuses) & (Ticket.support_level == TicketLevel.L2) & (Ticket.sla_due_at < now), 1), else_=0)).label("l2_breached"),
            func.sum(case((Ticket.status.in_(active_statuses) & (Ticket.support_level == TicketLevel.L3) & (Ticket.sla_due_at < now), 1), else_=0)).label("l3_breached"),
        )
        
        result = self._session.execute(stmt).first()

        return {
            "l1_active": int(getattr(result, 'l1_active', 0) or 0),
            "l2_active": int(getattr(result, 'l2_active', 0) or 0),
            "l3_active": int(getattr(result, 'l3_active', 0) or 0),
            "l1_unassigned": int(getattr(result, 'l1_unassigned', 0) or 0),
            "l2_unassigned": int(getattr(result, 'l2_unassigned', 0) or 0),
            "l3_unassigned": int(getattr(result, 'l3_unassigned', 0) or 0),
            "l1_breached": int(getattr(result, 'l1_breached', 0) or 0),
            "l2_breached": int(getattr(result, 'l2_breached', 0) or 0),
            "l3_breached": int(getattr(result, 'l3_breached', 0) or 0),
        }

    def get_engineer_workloads(self) -> list[dict]:
        from datetime import datetime, timezone
        from sqlalchemy import case, func
        from app.models.user import User
        from app.models.user_role import user_roles
        from app.models.role import Role
        from app.models.ticket import TicketPriority
        
        now = datetime.now(timezone.utc)
        active_statuses = [TicketStatus.OPEN, TicketStatus.IN_PROGRESS]
        
        stmt = (
            select(
                User.id.label("user_id"),
                User.full_name.label("full_name"),
                Role.name.label("role_name"),
                func.sum(case((Ticket.status.in_(active_statuses), 1), else_=0)).label("assigned_tickets"),
                func.sum(case((Ticket.status.in_(active_statuses) & (Ticket.priority == TicketPriority.CRITICAL), 1), else_=0)).label("critical_tickets"),
                func.sum(case((Ticket.status.in_(active_statuses) & (Ticket.sla_due_at < now), 1), else_=0)).label("breached_tickets"),
            )
            .join(user_roles, User.id == user_roles.c.user_id)
            .join(Role, user_roles.c.role_id == Role.id)
            .outerjoin(Ticket, Ticket.assigned_to_id == User.id)
            .where(Role.name.like("SUPPORT_%"))
            .group_by(User.id, User.full_name, Role.name)
        )
        
        results = self._session.execute(stmt).all()
        
        workloads = []
        for row in results:
            workloads.append({
                "user_id": row.user_id,
                "full_name": row.full_name,
                "role": row.role_name,
                "assigned_tickets": int(getattr(row, 'assigned_tickets', 0) or 0),
                "critical_tickets": int(getattr(row, 'critical_tickets', 0) or 0),
                "breached_tickets": int(getattr(row, 'breached_tickets', 0) or 0),
            })
            
        return workloads

    def get_ticket_distribution_stats(self) -> dict:
        by_status = dict(self._session.execute(
            select(Ticket.status, func.count(Ticket.id)).group_by(Ticket.status)
        ).all())
        by_priority = dict(self._session.execute(
            select(Ticket.priority, func.count(Ticket.id)).group_by(Ticket.priority)
        ).all())
        by_level = dict(self._session.execute(
            select(Ticket.support_level, func.count(Ticket.id)).group_by(Ticket.support_level)
        ).all())

        return {
            "by_status": {k.value: v for k, v in by_status.items()},
            "by_priority": {k.value: v for k, v in by_priority.items()},
            "by_level": {k.value: v for k, v in by_level.items()},
        }

    def get_sla_analytics(self) -> dict:
        from datetime import datetime, timezone
        from sqlalchemy import case, func
        now = datetime.now(timezone.utc)
        active_statuses = [TicketStatus.OPEN, TicketStatus.IN_PROGRESS]
        
        at_risk_cond = (
            Ticket.status.in_(active_statuses) & 
            (Ticket.sla_due_at >= now) & 
            ((func.extract('epoch', Ticket.sla_due_at) - now.timestamp()) <= 
             (func.extract('epoch', Ticket.sla_due_at) - func.extract('epoch', Ticket.created_at)) * 0.25)
        )
        
        breached_cond = (Ticket.status.in_(active_statuses)) & (Ticket.sla_due_at < now)
        
        healthy_cond = (
            Ticket.status.in_(active_statuses) & 
            (Ticket.sla_due_at >= now) & 
            ((func.extract('epoch', Ticket.sla_due_at) - now.timestamp()) > 
             (func.extract('epoch', Ticket.sla_due_at) - func.extract('epoch', Ticket.created_at)) * 0.25)
        )

        stmt = select(
            func.sum(case((Ticket.status.in_(active_statuses), 1), else_=0)).label("total_active"),
            func.sum(case((breached_cond, 1), else_=0)).label("breached"),
            func.sum(case((at_risk_cond, 1), else_=0)).label("at_risk"),
            func.sum(case((healthy_cond, 1), else_=0)).label("healthy"),
            func.count(Ticket.id).label("total_tickets"),
            func.sum(case((
                (Ticket.status.in_([TicketStatus.RESOLVED, TicketStatus.CLOSED]) & (Ticket.closed_at <= Ticket.sla_due_at)) |
                (Ticket.status.in_(active_statuses) & (Ticket.sla_due_at >= now)), 1
            ), else_=0)).label("compliant_count")
        )
        
        result = self._session.execute(stmt).first()
        
        total_active = int(getattr(result, 'total_active', 0) or 0)
        breached = int(getattr(result, 'breached', 0) or 0)
        at_risk = int(getattr(result, 'at_risk', 0) or 0)
        healthy = int(getattr(result, 'healthy', 0) or 0)
        total_tickets = int(getattr(result, 'total_tickets', 0) or 0)
        compliant_count = int(getattr(result, 'compliant_count', 0) or 0)
        
        sla_compliance_percent = round((compliant_count / max(1, total_tickets)) * 100, 1)

        return {
            "total_active": total_active,
            "breached": breached,
            "healthy": healthy,
            "at_risk": at_risk,
            "sla_compliance_percent": sla_compliance_percent,
        }

    def get_resolution_analytics(self) -> dict:
        closed_tickets = self._session.execute(
            select(Ticket.created_at, Ticket.closed_at)
            .where(Ticket.status.in_([TicketStatus.RESOLVED, TicketStatus.CLOSED]))
            .where(Ticket.closed_at.is_not(None))
        ).all()
        
        if not closed_tickets:
            return {"average_resolution_hours": None}
            
        total_hours = 0
        for created, closed in closed_tickets:
            total_hours += (closed - created).total_seconds() / 3600.0
            
        avg = round(total_hours / len(closed_tickets), 1)
        return {"average_resolution_hours": avg}

    def get_escalation_analytics(self) -> dict:
        from app.models.audit_log import AuditLog
        
        escalations = self._session.execute(
            select(AuditLog.event_metadata)
            .where(AuditLog.action == "TICKET_ESCALATED")
        ).scalars().all()
        
        total = len(escalations)
        l1_to_l2 = 0
        l2_to_l3 = 0
        
        for meta in escalations:
            if not meta:
                continue
            if meta.get("from_level") == "L1" and meta.get("to_level") == "L2":
                l1_to_l2 += 1
            elif meta.get("from_level") == "L2" and meta.get("to_level") == "L3":
                l2_to_l3 += 1
                
        total_tickets = self._session.execute(select(func.count(Ticket.id))).scalar() or 0
        avg_per_ticket = round(total / max(1, total_tickets), 1)
        
        return {
            "total_escalations": total,
            "l1_to_l2": l1_to_l2,
            "l2_to_l3": l2_to_l3,
            "avg_escalations_per_ticket": avg_per_ticket,
        }

    def get_workload_analytics(self) -> dict:
        workloads = self.get_engineer_workloads()
        if not workloads:
            return {
                "max_assigned": 0,
                "avg_assigned": 0.0,
                "unassigned": 0,
                "workload_distribution": {}
            }
            
        assigned_counts = [w["assigned_tickets"] for w in workloads]
        max_assigned = max(assigned_counts)
        avg_assigned = round(sum(assigned_counts) / len(assigned_counts), 1)
        
        unassigned = self._session.execute(
            select(func.count(Ticket.id))
            .where(Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS]))
            .where(Ticket.assigned_to_id.is_(None))
        ).scalar() or 0
        
        distribution = {w["full_name"]: w["assigned_tickets"] for w in workloads}
        
        return {
            "max_assigned": max_assigned,
            "avg_assigned": avg_assigned,
            "unassigned": unassigned,
            "workload_distribution": distribution,
        }

    def get_open_vs_closed_ratio(self) -> float:
        total_tickets = self._session.execute(select(func.count(Ticket.id))).scalar() or 0
        open_tickets = self._session.execute(
            select(func.count(Ticket.id))
            .where(Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS]))
        ).scalar() or 0
        
        closed_tickets = total_tickets - open_tickets
        return round(open_tickets / closed_tickets, 2) if closed_tickets > 0 else float(open_tickets)
