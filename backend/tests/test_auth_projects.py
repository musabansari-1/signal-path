from fastapi.testclient import TestClient


def register(client: TestClient, email: str = "dev@example.com") -> dict[str, object]:
    response = client.post(
        "/api/auth/register",
        json={"email": email, "password": "honest-search-123", "full_name": "Dev Candidate"},
    )
    assert response.status_code == 201
    return response.json()


def test_register_login_refresh_and_logout(client: TestClient) -> None:
    user = register(client)
    assert user["email"] == "dev@example.com"
    assert client.get("/api/auth/me").status_code == 200

    login = client.post(
        "/api/auth/login",
        json={"email": "dev@example.com", "password": "honest-search-123"},
    )
    assert login.status_code == 200
    assert client.post("/api/auth/refresh").status_code == 200
    assert client.post("/api/auth/logout").status_code == 204
    assert client.get("/api/auth/me").status_code == 401


def test_duplicate_email_is_rejected(client: TestClient) -> None:
    register(client)
    response = client.post(
        "/api/auth/register",
        json={"email": "DEV@example.com", "password": "another-safe-pass", "full_name": "Other"},
    )
    assert response.status_code == 409


def test_project_crud_and_active_selection(client: TestClient) -> None:
    register(client)
    created = client.post(
        "/api/projects",
        json={
            "name": "Backend search",
            "target_role": "Backend engineer",
            "target_location": "Remote",
        },
    )
    assert created.status_code == 201
    project_id = created.json()["id"]
    assert client.get("/api/auth/me").json()["active_project_id"] == project_id

    updated = client.patch(
        f"/api/projects/{project_id}", json={"target_industry": "Developer tools"}
    )
    assert updated.status_code == 200
    assert updated.json()["target_industry"] == "Developer tools"
    assert len(client.get("/api/projects").json()) == 1
    assert client.delete(f"/api/projects/{project_id}").status_code == 204


def test_project_ownership_is_enforced(client: TestClient) -> None:
    register(client, "first@example.com")
    project_id = client.post(
        "/api/projects", json={"name": "Private search", "target_role": "Engineer"}
    ).json()["id"]
    client.post("/api/auth/logout")
    register(client, "second@example.com")

    assert client.get(f"/api/projects/{project_id}").status_code == 404
    assert client.patch(f"/api/projects/{project_id}", json={"name": "Nope"}).status_code == 404

