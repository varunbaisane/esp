from app.db.session import SessionLocal
from app.repositories.ticket_repository import TicketRepository
try:
    db = SessionLocal()
    repo = TicketRepository(db)
    print("Testing stats...")
    print(repo.get_team_operations_stats())
    print("Testing workloads...")
    print(repo.get_engineer_workloads())
except Exception as e:
    import traceback
    traceback.print_exc()
