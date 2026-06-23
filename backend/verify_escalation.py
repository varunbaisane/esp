import requests

BASE_URL = "http://localhost:8000/api/v1"
HEADERS = {"Content-Type": "application/json"}

import random

# 1. Register and Login to get token
email = f"test{random.randint(1000,9999)}@example.com"
register_data = {"email": email, "password": "password123", "full_name": "Test User"}
requests.post(f"{BASE_URL}/auth/register", json=register_data)

login_data = {"email": email, "password": "password123"}
r_login = requests.post(f"{BASE_URL}/auth/login", json=login_data)
if r_login.status_code != 200:
    print(f"Login failed: {r_login.text}")
    exit(1)

token = r_login.json()["access_token"]
HEADERS["Authorization"] = f"Bearer {token}"

# 2. Create ticket
ticket_data = {
    "title": "Escalation Test Ticket",
    "description": "Testing L1 -> L2 -> L3",
    "priority": "MEDIUM"
}
r_create = requests.post(f"{BASE_URL}/tickets", json=ticket_data, headers=HEADERS)
if r_create.status_code != 201:
    print(f"Failed to create ticket: {r_create.text}")
    exit(1)

ticket = r_create.json()
ticket_id = ticket["id"]
print(f"Created ticket {ticket_id} with level {ticket['support_level']}")
assert ticket["support_level"] == "L1"

# 3. Escalate L1 -> L2
r_esc1 = requests.post(f"{BASE_URL}/tickets/{ticket_id}/escalate", headers=HEADERS)
if r_esc1.status_code != 200:
    print(f"Failed L1 -> L2: {r_esc1.text}")
    exit(1)
ticket = r_esc1.json()
print(f"Escalated to {ticket['support_level']}")
assert ticket["support_level"] == "L2"

# 4. Escalate L2 -> L3
r_esc2 = requests.post(f"{BASE_URL}/tickets/{ticket_id}/escalate", headers=HEADERS)
if r_esc2.status_code != 200:
    print(f"Failed L2 -> L3: {r_esc2.text}")
    exit(1)
ticket = r_esc2.json()
print(f"Escalated to {ticket['support_level']}")
assert ticket["support_level"] == "L3"

# 5. Escalate L3 -> Fail
r_esc3 = requests.post(f"{BASE_URL}/tickets/{ticket_id}/escalate", headers=HEADERS)
print(f"Attempt L3 -> ?: Status {r_esc3.status_code}")
assert r_esc3.status_code == 400

print("Verification complete!")
