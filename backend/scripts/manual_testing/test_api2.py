from app.db.session import SessionLocal
from app.repositories.user_repository import UserRepository

db = SessionLocal()
repo = UserRepository(db)
admin_user = repo.get_by_email("admin@esp.local")
print(admin_user.roles)
for role in admin_user.roles:
    print(role.name)
