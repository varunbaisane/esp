from fastapi.testclient import TestClient # pyrefly: ignore [missing-import]

def create_user(client: TestClient, email: str = "test@example.com", full_name: str = "Test User") -> dict:
    response = client.post(
        "/api/v1/users",
        json={"email": email, "full_name": full_name}
    )
    assert response.status_code == 201
    return response.json()

def create_role(client: TestClient, name: str = "Admin") -> dict:
    response = client.post(
        "/api/v1/roles",
        json={"name": name}
    )
    assert response.status_code == 201
    return response.json()

def assign_role(client: TestClient, user_id: int, role_id: int) -> dict:
    response = client.post(
        f"/api/v1/users/{user_id}/roles",
        json={"role_id": role_id}
    )
    assert response.status_code == 201
    return response.json()

def create_ticket(client: TestClient, created_by_id: int, title: str = "Test Ticket", description: str = "Test Desc") -> dict:
    response = client.post(
        "/api/v1/tickets",
        json={"title": title, "description": description, "created_by_id": created_by_id}
    )
    assert response.status_code == 201
    return response.json()
