from unittest.mock import AsyncMock

import pytest

from app.api.dependency.dependencies import get_email_service
from app.services.email_service import EmailService


@pytest.fixture(autouse=True)
def mock_email_service():
    email_service = AsyncMock(spec=EmailService)

    return_value = None
    email_service.send_ticket_created.return_value = return_value
    email_service.send_ticket_closed.return_value = return_value

    from app.main import app

    app.dependency_overrides[get_email_service] = lambda: email_service

    yield email_service

    app.dependency_overrides.pop(get_email_service, None)


# Helper function
def create_ticket(client, headers, title="Keyboard not working"):
    return client.post(
        "/tickets",
        json={
            "title": title,
            "description": "Some keyboard keys are not working",
            "priority": "medium",
            "issue_type": "HARDWARE",
        },
        headers=headers,
    )


# 1. Create ticket successfully
def test_create_ticket(client, employee_headers):
    response = create_ticket(client, employee_headers)

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Keyboard not working"
    assert data["priority"] == "medium"
    assert data["status"] == "open"
    assert data["requires_approval"] is False
    assert data["ticket_number"] is not None
    assert data["user_id"] is not None


# 2. Create ticket with invalid data
def test_create_ticket_invalid_data(client, employee_headers):
    response = client.post(
        "/tickets",
        json={
            "title": "AB",
            "description": "Invalid ticket",
            "priority": "urgent",
            "issue_type": "INVALID",
        },
        headers=employee_headers,
    )

    assert response.status_code == 422


# 3. Create ticket without authentication
def test_create_ticket_without_token(client):
    response = client.post(
        "/tickets",
        json={
            "title": "Network issue",
            "description": "Internet is not working",
            "priority": "high",
            "issue_type": "NETWORK",
        },
    )

    assert response.status_code == 401


# 4. Employee cannot create ticket as admin
def test_admin_cannot_create_ticket(client, admin_headers):
    response = create_ticket(client, admin_headers)

    assert response.status_code == 403


# 5. Get employee's own tickets
def test_get_my_tickets(client, employee_headers):
    create_ticket(client, employee_headers)

    response = client.get(
        "/tickets/my-tickets",
        headers=employee_headers,
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


# 6. Admin cannot access employee's my-tickets endpoint
def test_admin_cannot_get_my_tickets(client, admin_headers):
    response = client.get(
        "/tickets/my-tickets",
        headers=admin_headers,
    )

    assert response.status_code == 403


# 7. Admin gets all tickets
def test_get_all_tickets(client, employee_headers, admin_headers):
    create_ticket(client, employee_headers)

    response = client.get(
        "/tickets/all-tickets",
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


# 8. Employee cannot get all tickets
def test_employee_cannot_get_all_tickets(client, employee_headers):
    response = client.get(
        "/tickets/all-tickets",
        headers=employee_headers,
    )

    assert response.status_code == 403


# 9. Get overdue tickets
def test_get_overdue_tickets(client, admin_headers):
    response = client.get(
        "/tickets/overdue",
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


# 10. Get ticket by ID
def test_get_ticket_by_id(client, employee_headers):
    create_response = create_ticket(client, employee_headers)

    ticket_id = create_response.json()["id"]

    response = client.get(
        f"/tickets/{ticket_id}",
        headers=employee_headers,
    )

    assert response.status_code == 200
    assert response.json()["id"] == ticket_id


# 11. Get nonexistent ticket
def test_get_nonexistent_ticket(client, employee_headers):
    response = client.get(
        "/tickets/9999",
        headers=employee_headers,
    )

    assert response.status_code == 404


# 12. Update ticket status
def test_update_ticket_status(
    client,
    employee_headers,
    admin_headers,
):
    create_response = create_ticket(client, employee_headers)

    ticket_id = create_response.json()["id"]

    response = client.patch(
        f"/tickets/{ticket_id}/status",
        json={
            "status": "in_progress",
            "status_change_remark": "Work has started",
        },
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"


# 13. Employee cannot update ticket status
def test_employee_cannot_update_ticket_status(
    client,
    employee_headers,
):
    create_response = create_ticket(client, employee_headers)

    ticket_id = create_response.json()["id"]

    response = client.patch(
        f"/tickets/{ticket_id}/status",
        json={
            "status": "in_progress",
            "status_change_remark": "Starting work",
        },
        headers=employee_headers,
    )

    assert response.status_code == 403


# 14. Close resolved ticket
def test_close_ticket(client, employee_headers, admin_headers):
    create_response = create_ticket(client, employee_headers)

    ticket_id = create_response.json()["id"]

    # First resolve the ticket
    resolve_response = client.patch(
        f"/tickets/{ticket_id}/status",
        json={
            "status": "resolved",
            "status_change_remark": "Issue fixed",
        },
        headers=admin_headers,
    )

    assert resolve_response.status_code == 200

    # Then close the ticket
    response = client.patch(
        f"/tickets/{ticket_id}/close",
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "closed"


# 15. Cannot close unresolved ticket
def test_close_unresolved_ticket(
    client,
    employee_headers,
    admin_headers,
):
    create_response = create_ticket(client, employee_headers)

    ticket_id = create_response.json()["id"]

    response = client.patch(
        f"/tickets/{ticket_id}/close",
        headers=admin_headers,
    )

    assert response.status_code == 409


# 16. Close nonexistent ticket
def test_close_nonexistent_ticket(client, admin_headers):
    response = client.patch(
        "/tickets/9999/close",
        headers=admin_headers,
    )

    assert response.status_code == 404
