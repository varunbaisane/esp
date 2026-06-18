from tests.helpers import create_user, create_ticket

def test_create_ticket(client):
    user = create_user(client)
    ticket = create_ticket(client, user["id"])
    assert ticket["title"] == "Test Ticket"
    assert ticket["status"] == "OPEN"
    assert ticket["created_by_id"] == user["id"]
    assert ticket["assigned_to_id"] is None

def test_get_ticket(client):
    user = create_user(client)
    ticket = create_ticket(client, user["id"])
    response = client.get(f"/api/v1/tickets/{ticket['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == ticket["id"]

def test_list_tickets(client):
    user = create_user(client)
    create_ticket(client, user["id"], title="Ticket 1")
    create_ticket(client, user["id"], title="Ticket 2")
    response = client.get("/api/v1/tickets")
    assert response.status_code == 200
    assert len(response.json()) >= 2

def test_assign_ticket(client):
    user1 = create_user(client, email="1@example.com")
    user2 = create_user(client, email="2@example.com")
    ticket = create_ticket(client, user1["id"])
    
    response = client.post(
        f"/api/v1/tickets/{ticket['id']}/assign",
        json={"user_id": user2["id"]}
    )
    assert response.status_code == 200
    assert response.json()["assigned_to_id"] == user2["id"]

def test_reassign_ticket(client):
    user1 = create_user(client, email="1@example.com")
    user2 = create_user(client, email="2@example.com")
    ticket = create_ticket(client, user1["id"])
    
    client.post(f"/api/v1/tickets/{ticket['id']}/assign", json={"user_id": user2["id"]})
    response = client.post(f"/api/v1/tickets/{ticket['id']}/assign", json={"user_id": user1["id"]})
    assert response.status_code == 200
    assert response.json()["assigned_to_id"] == user1["id"]

def test_assign_missing_ticket(client):
    user = create_user(client)
    response = client.post(
        "/api/v1/tickets/999/assign",
        json={"user_id": user["id"]}
    )
    assert response.status_code == 404

def test_assign_missing_user(client):
    user = create_user(client)
    ticket = create_ticket(client, user["id"])
    response = client.post(
        f"/api/v1/tickets/{ticket['id']}/assign",
        json={"user_id": 999}
    )
    assert response.status_code == 400

def test_status_workflow(client):
    user = create_user(client)
    ticket = create_ticket(client, user["id"])
    
    # OPEN -> IN_PROGRESS
    res = client.post(f"/api/v1/tickets/{ticket['id']}/status", json={"status": "IN_PROGRESS"})
    assert res.status_code == 200
    assert res.json()["status"] == "IN_PROGRESS"

    # IN_PROGRESS -> RESOLVED
    res = client.post(f"/api/v1/tickets/{ticket['id']}/status", json={"status": "RESOLVED"})
    assert res.status_code == 200
    assert res.json()["status"] == "RESOLVED"

    # RESOLVED -> CLOSED
    res = client.post(f"/api/v1/tickets/{ticket['id']}/status", json={"status": "CLOSED"})
    assert res.status_code == 200
    assert res.json()["status"] == "CLOSED"

def test_invalid_transition(client):
    user = create_user(client)
    ticket = create_ticket(client, user["id"])
    
    # OPEN -> CLOSED
    res = client.post(f"/api/v1/tickets/{ticket['id']}/status", json={"status": "CLOSED"})
    assert res.status_code == 400

def test_dashboard_queries(client):
    user1 = create_user(client, email="dash1@example.com")
    user2 = create_user(client, email="dash2@example.com")
    
    t1 = create_ticket(client, user1["id"], title="T1")
    t2 = create_ticket(client, user1["id"], title="T2")
    t3 = create_ticket(client, user2["id"], title="T3")
    
    client.post(f"/api/v1/tickets/{t1['id']}/assign", json={"user_id": user1["id"]})
    
    client.post(f"/api/v1/tickets/{t2['id']}/assign", json={"user_id": user1["id"]})
    client.post(f"/api/v1/tickets/{t2['id']}/status", json={"status": "IN_PROGRESS"})
    
    client.post(f"/api/v1/tickets/{t3['id']}/assign", json={"user_id": user2["id"]})
    client.post(f"/api/v1/tickets/{t3['id']}/status", json={"status": "IN_PROGRESS"})
    client.post(f"/api/v1/tickets/{t3['id']}/status", json={"status": "RESOLVED"})
    client.post(f"/api/v1/tickets/{t3['id']}/status", json={"status": "CLOSED"})
    
    # GET /tickets/stats
    res = client.get("/api/v1/tickets/stats")
    assert res.status_code == 200
    stats = res.json()
    assert stats["open"] == 1
    assert stats["in_progress"] == 1
    assert stats["resolved"] == 0
    assert stats["closed"] == 1
    assert stats["total"] == 3
    
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

