from tests.helpers import create_user, create_role, assign_role

def test_assign_role(client):
    user = create_user(client)
    role = create_role(client)
    assignment = assign_role(client, user["id"], role["id"])
    assert assignment["user_id"] == user["id"]
    assert assignment["role_id"] == role["id"]

def test_duplicate_assignment(client):
    user = create_user(client)
    role = create_role(client)
    assign_role(client, user["id"], role["id"])
    
    # Try assigning the exact same role again
    response = client.patch(
        f"/api/v1/users/{user['id']}/roles",
        json={"operation": "assign", "role_code": "SUPPORT_L1"}
    )
    # The backend handles this gracefully now by deleting old roles and inserting new ones,
    # or it might throw a 400 depending on exact logic. Let's see what happens.
    # Actually, RoleProvisioningService deletes all UserRole entries for that user and inserts the new one.
    # So duplicate assignment just succeeds by overwriting it!
    assert response.status_code == 200

def test_get_user_roles(client):
    # This endpoint GET /api/v1/users/{user_id}/roles was removed.
    # Instead, we test that the user's role shows up in the user summary.
    user = create_user(client)
    role1 = create_role(client, "SUPPORT_L2")
    role2 = create_role(client, "SUPPORT_L3")
    
    assign_role(client, user["id"], role1["id"])
    
    response = client.get(f"/api/v1/users/{user['id']}")
    assert response.status_code == 200
    # UserRead includes roles
    user_data = response.json()
    assert len(user_data["roles"]) == 1
    assert user_data["roles"][0]["name"] == "SUPPORT_L2"

def test_get_role_users(client):
    user1 = create_user(client, email="1@example.com")
    user2 = create_user(client, email="2@example.com")
    role = create_role(client)
    
    assign_role(client, user1["id"], role["id"])
    assign_role(client, user2["id"], role["id"])
    
    response = client.get(f"/api/v1/roles/{role['id']}/users")
    assert response.status_code == 200
    assert len(response.json()) == 2
