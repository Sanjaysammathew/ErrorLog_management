import pytest

# Authentication fixtures


@pytest.fixture
def admin_headers(client):
    response = client.post(
        "/auth/login",
        data={
            "username": "admin",
            "password": "admin123",
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def manager_headers(client):
    response = client.post(
        "/auth/login",
        data={
            "username": "manager",
            "password": "manager123",
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


# Helper to create a category


def create_category(client, headers, name="Hardware Issue"):
    return client.post(
        "/categories",
        json={
            "name": name,
            "issue_type": "HARDWARE",
            "description": "Hardware related problems",
            "default_sla_hours": 24,
            "requires_approval_default": False,
        },
        headers=headers,
    )


# 1. Create category


def test_create_category(client, admin_headers):
    response = create_category(client, admin_headers)

    assert response.status_code == 201
    assert response.json()["name"] == "Hardware Issue"
    assert response.json()["issue_type"] == "HARDWARE"
    assert response.json()["default_sla_hours"] == 24
    assert response.json()["is_active"] is True


# 2. Create duplicate category


def test_create_duplicate_category(client, admin_headers):
    create_category(client, admin_headers)

    response = create_category(client, admin_headers)

    assert response.status_code == 409


# 3. Create category with invalid data


def test_create_category_invalid_data(client, admin_headers):
    response = client.post(
        "/categories",
        json={
            "name": "H",
            "issue_type": "INVALID",
            "default_sla_hours": 0,
        },
        headers=admin_headers,
    )

    assert response.status_code == 422


# 4. Get all categories


def test_get_all_categories(client, admin_headers):
    create_category(client, admin_headers)

    response = client.get(
        "/categories",
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


# 5. Get category by ID


def test_get_category_by_id(client, admin_headers):
    create_response = create_category(client, admin_headers)

    category_id = create_response.json()["id"]

    response = client.get(
        f"/categories/{category_id}",
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["id"] == category_id
    assert response.json()["name"] == "Hardware Issue"


# 6. Update category


def test_update_category(client, admin_headers):
    create_response = create_category(client, admin_headers)

    category_id = create_response.json()["id"]

    response = client.put(
        f"/categories/{category_id}",
        json={
            "name": "Updated Hardware",
            "default_sla_hours": 48,
        },
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Hardware"
    assert response.json()["default_sla_hours"] == 48


# 7. Update nonexistent category


def test_update_nonexistent_category(client, admin_headers):
    response = client.put(
        "/categories/9999",
        json={"name": "Updated Category"},
        headers=admin_headers,
    )

    assert response.status_code == 404


# 8. Deactivate category


def test_deactivate_category(client, admin_headers):
    create_response = create_category(client, admin_headers)

    category_id = create_response.json()["id"]

    response = client.patch(
        f"/categories/{category_id}/deactivate",
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False


# 9. Deactivate nonexistent category


def test_deactivate_nonexistent_category(client, admin_headers):
    response = client.patch(
        "/categories/9999/deactivate",
        headers=admin_headers,
    )

    assert response.status_code == 404


# 10. Employee/manager role can view categories
# Manager is already available in your test database.


def test_manager_can_view_categories(client, manager_headers):
    response = client.get(
        "/categories",
        headers=manager_headers,
    )

    assert response.status_code == 200


# 11. Manager cannot create category


def test_manager_cannot_create_category(client, manager_headers):
    response = create_category(client, manager_headers)

    assert response.status_code == 403


# 12. Unauthenticated user cannot create category


def test_create_category_without_token(client):
    response = client.post(
        "/categories",
        json={
            "name": "Network Issue",
            "issue_type": "NETWORK",
        },
    )

    assert response.status_code == 401
