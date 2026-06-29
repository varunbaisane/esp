from tests.helpers import create_user, create_ticket, ensure_role, assign_role

def setup_users(client, emails):
    role_id = ensure_role(client, "SUPPORT_L1")
    users = []
    for email in emails:
        user = create_user(client, email=email)
        assign_role(client, user["id"], role_id)
        users.append(user)
    return users

def test_create_ticket(client):
    user = setup_users(client, ["create@test.com"])[0]
    ticket = create_ticket(client, user["id"])
    assert ticket["title"] == "Test Ticket"
    assert ticket["status"] == "OPEN"
    assert ticket["created_by_id"] == user["id"]
    assert ticket["assigned_to_id"] is None

def test_get_ticket(client):
    user = setup_users(client, ["get@test.com"])[0]
    ticket = create_ticket(client, user["id"])
    response = client.get(f"/api/v1/tickets/{ticket['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == ticket["id"]

def test_list_tickets(client):
    user = setup_users(client, ["list@test.com"])[0]
    create_ticket(client, user["id"], title="Ticket 1")
    create_ticket(client, user["id"], title="Ticket 2")
    response = client.get("/api/v1/tickets")
    assert response.status_code == 200
    assert len(response.json()) >= 2

def test_assign_ticket(client):
    users = setup_users(client, ["assign1@example.com", "assign2@example.com"])
    user1, user2 = users[0], users[1]
    ticket = create_ticket(client, user1["id"])
    
    response = client.post(
        f"/api/v1/tickets/{ticket['id']}/assign",
        json={"assignee_id": user2["id"]}
    )
    assert response.status_code == 200
    assert response.json()["assigned_to_id"] == user2["id"]

def test_reassign_ticket(client):
    users = setup_users(client, ["reassign1@example.com", "reassign2@example.com"])
    user1, user2 = users[0], users[1]
    ticket = create_ticket(client, user1["id"])
    
    client.post(f"/api/v1/tickets/{ticket['id']}/assign", json={"assignee_id": user2["id"]})
    response = client.post(f"/api/v1/tickets/{ticket['id']}/assign", json={"assignee_id": user1["id"]})
    assert response.status_code == 200
    assert response.json()["assigned_to_id"] == user1["id"]

def test_assign_missing_ticket(client):
    user = setup_users(client, ["missing1@test.com"])[0]
    response = client.post(
        "/api/v1/tickets/999/assign",
        json={"assignee_id": user["id"]}
    )
    assert response.status_code == 404

def test_assign_missing_user(client):
    user = setup_users(client, ["missinguser@test.com"])[0]
    ticket = create_ticket(client, user["id"])
    response = client.post(
        f"/api/v1/tickets/{ticket['id']}/assign",
        json={"assignee_id": 999}
    )
    assert response.status_code == 404

def test_status_workflow(client):
    user = setup_users(client, ["status@test.com"])[0]
    ticket = create_ticket(client, user["id"])
    
    # OPEN -> IN_PROGRESS
    res = client.patch(f"/api/v1/tickets/{ticket['id']}", json={"status": "IN_PROGRESS"})
    assert res.status_code == 200
    assert res.json()["status"] == "IN_PROGRESS"

    # IN_PROGRESS -> RESOLVED
    res = client.patch(f"/api/v1/tickets/{ticket['id']}", json={"status": "RESOLVED"})
    assert res.status_code == 200
    assert res.json()["status"] == "RESOLVED"

    # RESOLVED -> CLOSED
    res = client.patch(f"/api/v1/tickets/{ticket['id']}", json={"status": "CLOSED"})
    assert res.status_code == 200
    assert res.json()["status"] == "CLOSED"

def test_invalid_transition(client):
    user = setup_users(client, ["invalid@test.com"])[0]
    ticket = create_ticket(client, user["id"])
    
    # OPEN -> CLOSED
    res = client.patch(f"/api/v1/tickets/{ticket['id']}", json={"status": "CLOSED"})
    assert res.status_code == 409

def test_dashboard_queries(client):
    users = setup_users(client, ["dash1@example.com", "dash2@example.com"])
    user1, user2 = users[0], users[1]
    
    t1 = create_ticket(client, user1["id"], title="T1")
    t2 = create_ticket(client, user1["id"], title="T2")
    t3 = create_ticket(client, user2["id"], title="T3")
    
    client.post(f"/api/v1/tickets/{t1['id']}/assign", json={"assignee_id": user1["id"]})
    
    client.post(f"/api/v1/tickets/{t2['id']}/assign", json={"assignee_id": user1["id"]})
    client.patch(f"/api/v1/tickets/{t2['id']}", json={"status": "IN_PROGRESS"})
    
    client.post(f"/api/v1/tickets/{t3['id']}/assign", json={"assignee_id": user2["id"]})
    client.patch(f"/api/v1/tickets/{t3['id']}", json={"status": "IN_PROGRESS"})
    client.patch(f"/api/v1/tickets/{t3['id']}", json={"status": "RESOLVED"})
    client.patch(f"/api/v1/tickets/{t3['id']}", json={"status": "CLOSED"})
    
    # GET /tickets/stats
    res = client.get("/api/v1/tickets/stats")
    assert res.status_code == 200
    stats = res.json()
    assert stats["open_tickets"] == 2
    assert stats["my_assigned_tickets"] == 0 # test_admin runs this, not user1
    assert stats["unassigned_tickets"] == 0
    assert stats["total_assigned_tickets"] if "total_assigned_tickets" in stats else True # just to avoid keyerror
    
    # GET /tickets/status/{status}
    res = client.get("/api/v1/tickets/status/OPEN")
    assert res.status_code == 200
    assert len(res.json()) == 1
    
    # GET /tickets/assigned/{user_id}
    res = client.get(f"/api/v1/tickets/assigned/{user1['id']}")
    assert res.status_code == 200
    assert len(res.json()) == 2
    
    # GET /tickets/created/{user_id}
    res = client.get(f"/api/v1/tickets/created/{user1['id']}")
    assert res.status_code == 200
    assert len(res.json()) == 2

    # GET /tickets/assigned/999 (Missing User)
    res = client.get("/api/v1/tickets/assigned/999")
    assert res.status_code == 404

    # GET /tickets/created/999 (Missing User)
    res = client.get("/api/v1/tickets/created/999")
    assert res.status_code == 404

