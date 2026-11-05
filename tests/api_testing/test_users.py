import pytest


# Helper: create an authenticated admin
@pytest.fixture
def admin_headers(client):
    # Login using your existing admin account.
    response = client.post(
        "/auth/login",
        data={
            "username": "admin@example.com",
            "password": "admin123",
        },
    )

    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


# 1. Create user
def test_create_user(client, admin_headers):
    response = client.post(
        "/users",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "Test@123",
            "role": "employee",
        },
        headers=admin_headers,
    )

    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"


# 2. Get all users
def test_list_users(client, admin_headers):
    response = client.get(
        "/users",
        params={"page": 1, "page_size": 10},
        headers=admin_headers,
    )

    assert response.status_code == 200


# 3. Get user by ID
def test_get_user(client, admin_headers):
    create_response = client.post(
        "/users",
        json={
            "username": "anotheruser",
            "email": "another@example.com",
            "password": "Test@123",
            "role": "employee",
        },
        headers=admin_headers,
    )

    user_id = create_response.json()["id"]

    response = client.get(
        f"/users/{user_id}",
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["id"] == user_id


# 4. Update user
def test_update_user(client, admin_headers):
    create_response = client.post(
        "/users",
        json={
            "username": "olduser",
            "email": "old@example.com",
            "password": "Test@123",
            "role": "employee",
        },
        headers=admin_headers,
    )

    user_id = create_response.json()["id"]

    response = client.put(
        f"/users/{user_id}",
        json={
            "username": "updateduser",
            "email": "old@example.com",
            "role": "employee",
        },
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["username"] == "updateduser"


# 5. Patch user
def test_patch_user(client, admin_headers):
    create_response = client.post(
        "/users",
        json={
            "username": "patchuser",
            "email": "patch@example.com",
            "password": "Test@123",
            "role": "employee",
        },
        headers=admin_headers,
    )

    user_id = create_response.json()["id"]

    response = client.patch(
        f"/users/{user_id}",
        json={"username": "patcheduser"},
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["username"] == "patcheduser"


# 6. Deactivate user
def test_delete_user(client, admin_headers):
    create_response = client.post(
        "/users",
        json={
            "username": "deleteuser",
            "email": "delete@example.com",
            "password": "Test@123",
            "role": "employee",
        },
        headers=admin_headers,
    )

    user_id = create_response.json()["id"]

    response = client.delete(
        f"/users/{user_id}",
        headers=admin_headers,
    )

    assert response.status_code == 200


# 7. Unauthorized access
def test_list_users_without_token(client):
    response = client.get("/users")

    assert response.status_code in (401, 403)


# 8. Invalid pagination
def test_list_users_invalid_pagination(client, admin_headers):
    response = client.get(
        "/users?page=0",
        headers=admin_headers,
    )

    assert response.status_code == 422


def test_current_user_profile(client):
    login_response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "admin123"},
    )
    headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

    response = client.get("/users/me", headers=headers)

    assert response.status_code == 400
    assert response.json() == {"detail": "Provide either user_id or email."}

    response = client.get("/users/me?email=admin@example.com", headers=headers)

    assert response.status_code == 200
    assert response.json()["username"] == "admin"
    assert response.json()["email"] == "admin@example.com"
