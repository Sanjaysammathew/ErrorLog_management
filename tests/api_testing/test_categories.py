import pytest

from app.models.ErrorCategory import ErrorCategory, IssueType

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


async def seed_category(db_session, name="Hardware Issue"):
    category = ErrorCategory(
        name=name,
        issue_type=IssueType.HARDWARE,
        description="Hardware related problems",
        default_sla_hours=24,
        requires_approval_default=False,
        is_active=True,
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    return category


# 1. Get all categories


@pytest.mark.asyncio(loop_scope="session")
async def test_get_all_categories(client, admin_headers, db_session):
    await seed_category(db_session)

    response = client.get(
        "/categories",
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


# 2. Get category by ID


@pytest.mark.asyncio(loop_scope="session")
async def test_get_category_by_id(client, admin_headers, db_session):
    category = await seed_category(db_session)
    category_id = category.id

    response = client.get(
        f"/categories/{category_id}",
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["id"] == category_id
    assert response.json()["name"] == "Hardware Issue"


# 3. Update category


@pytest.mark.asyncio(loop_scope="session")
async def test_update_category(client, admin_headers, db_session):
    category = await seed_category(db_session)
    category_id = category.id

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


# 4. Update nonexistent category


def test_update_nonexistent_category(client, admin_headers):
    response = client.put(
        "/categories/9999",
        json={"name": "Updated Category"},
        headers=admin_headers,
    )

    assert response.status_code == 404


# 5. Deactivate category


@pytest.mark.asyncio(loop_scope="session")
async def test_deactivate_category(client, admin_headers, db_session):
    category = await seed_category(db_session)
    category_id = category.id

    response = client.patch(
        f"/categories/{category_id}/deactivate",
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False


# 6. Deactivate nonexistent category


def test_deactivate_nonexistent_category(client, admin_headers):
    response = client.patch(
        "/categories/9999/deactivate",
        headers=admin_headers,
    )

    assert response.status_code == 404


# 7. Employee/manager role can view categories
# Manager is already available in your test database.


def test_manager_can_view_categories(client, manager_headers):
    response = client.get(
        "/categories",
        headers=manager_headers,
    )

    assert response.status_code == 200
