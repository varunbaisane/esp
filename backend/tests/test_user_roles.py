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
    
    response = client.post(
        f"/api/v1/users/{user['id']}/roles",
        json={"role_id": role["id"]}
    )
    assert response.status_code == 400

def test_get_user_roles(client):
    user = create_user(client)
    role1 = create_role(client, "RoleA")
    role2 = create_role(client, "RoleB")
    
    assign_role(client, user["id"], role1["id"])
    assign_role(client, user["id"], role2["id"])
    
    response = client.get(f"/api/v1/users/{user['id']}/roles")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_get_role_users(client):
    user1 = create_user(client, email="1@example.com")
    user2 = create_user(client, email="2@example.com")
    role = create_role(client)
    
    assign_role(client, user1["id"], role["id"])
    assign_role(client, user2["id"], role["id"])
    
    response = client.get(f"/api/v1/roles/{role['id']}/users")
    assert response.status_code == 200
    assert len(response.json()) == 2
