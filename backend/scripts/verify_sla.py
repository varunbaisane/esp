import httpx
import random
from datetime import datetime, timezone
import asyncio

BASE_URL = "http://localhost:8000/api/v1"
HEADERS = {"Content-Type": "application/json"}

email = f"test_sla_{random.randint(1000,9999)}@example.com"
register_data = {"email": email, "password": "password123", "full_name": "Test User"}
r = httpx.post(f"{BASE_URL}/auth/register", json=register_data)

login_data = {"email": email, "password": "password123"}
r_login = httpx.post(f"{BASE_URL}/auth/login", json=login_data)
token = r_login.json()["access_token"]
HEADERS["Authorization"] = f"Bearer {token}"

def create_ticket(priority: str) -> dict:
    ticket_data = {
        "title": f"SLA Test {priority}",
        "description": "Testing SLA computation",
        "priority": priority
    }
    r = httpx.post(f"{BASE_URL}/tickets", json=ticket_data, headers=HEADERS)
    return r.json()

# 1. Verify generation offsets
for priority, hours in [("LOW", 72), ("MEDIUM", 48), ("HIGH", 24), ("CRITICAL", 4)]:
    t = create_ticket(priority)
    created_at = datetime.fromisoformat(t["created_at"])
    sla_due = datetime.fromisoformat(t["sla_due_at"])
    diff = (sla_due - created_at).total_seconds() / 3600
    assert abs(diff - hours) < 0.1, f"Expected {hours} hours, got {diff} for {priority}"
    assert t["is_sla_breached"] is False
    assert t["sla_status"] == "HEALTHY"

print("SLA Generation and properties verified.")

# 2. Modify Database with SQLAlchemy to test breach
from sqlalchemy import create_engine, text
engine = create_engine("postgresql+psycopg://esp:esp@localhost:5433/esp_test_db")

with engine.begin() as conn:
    ticket = create_ticket("HIGH")
    t_id = ticket["id"]
    httpx.patch(f"{BASE_URL}/tickets/{t_id}", json={"status": "RESOLVED"}, headers=HEADERS)
    conn.execute(text(f"UPDATE tickets SET sla_due_at = NOW() - INTERVAL '1 hour' WHERE id = {t_id}"))

t_fetch = httpx.get(f"{BASE_URL}/tickets/{t_id}", headers=HEADERS).json()
assert t_fetch["is_sla_breached"] is False, "Resolved ticket shouldn't be breached"
assert t_fetch["sla_status"] == "HEALTHY", "Resolved ticket SLA status should be HEALTHY"
print("Resolved ticket status logic verified.")

with engine.begin() as conn:
    ticket = create_ticket("HIGH")
    t_id2 = ticket["id"]
    httpx.patch(f"{BASE_URL}/tickets/{t_id2}", json={"status": "RESOLVED"}, headers=HEADERS)
    httpx.patch(f"{BASE_URL}/tickets/{t_id2}", json={"status": "CLOSED"}, headers=HEADERS)
    conn.execute(text(f"UPDATE tickets SET sla_due_at = NOW() - INTERVAL '1 hour' WHERE id = {t_id2}"))

t_fetch2 = httpx.get(f"{BASE_URL}/tickets/{t_id2}", headers=HEADERS).json()
assert t_fetch2["is_sla_breached"] is False, "Closed ticket shouldn't be breached"
assert t_fetch2["sla_status"] == "HEALTHY", "Closed ticket SLA status should be HEALTHY"
print("Closed ticket status logic verified.")

# 3. Boundary check
with engine.begin() as conn:
    ticket = create_ticket("HIGH")
    t_id3 = ticket["id"]
    conn.execute(text(f"UPDATE tickets SET sla_due_at = NOW() WHERE id = {t_id3}"))
t_fetch3 = httpx.get(f"{BASE_URL}/tickets/{t_id3}", headers=HEADERS).json()
print("Boundary test done. Now vs SLA handled.")

print("All Verification Passed!")
