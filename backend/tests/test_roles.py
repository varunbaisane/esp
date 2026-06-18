from tests.helpers import create_role

def test_create_role(client):
    role = create_role(client, "SuperAdmin")
    assert role["name"] == "SuperAdmin"
    assert "id" in role

def test_get_role(client):
    role = create_role(client)
    response = client.get(f"/api/v1/roles/{role['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == role["id"]

def test_list_roles(client):
    create_role(client, "Role1")
    create_role(client, "Role2")
    response = client.get("/api/v1/roles")
    assert response.status_code == 200
    assert len(response.json()) >= 2

def test_duplicate_name(client):
    create_role(client, "UniqueRole")
    response = client.post(
        "/api/v1/roles",
        json={"name": "UniqueRole"}
    )
    assert response.status_code == 400
