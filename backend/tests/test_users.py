from tests.helpers import create_user

def test_create_user(client):
    user = create_user(client)
    assert user["email"] == "test@example.com"
    assert user["full_name"] == "Test User"
    assert "id" in user

def test_duplicate_email(client):
    create_user(client, email="dup@example.com")
    response = client.post(
        "/api/v1/users",
        json={"email": "dup@example.com", "full_name": "Another User"}
    )
    assert response.status_code == 400

def test_get_user(client):
    user = create_user(client)
    response = client.get(f"/api/v1/users/{user['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == user["id"]

def test_list_users(client):
    create_user(client, email="user1@example.com")
    create_user(client, email="user2@example.com")
    response = client.get("/api/v1/users")
    assert response.status_code == 200
    assert len(response.json()) >= 2
