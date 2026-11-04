def create_ticket(client, employee_headers):
    response = client.post(
        "/tickets",
        json={
            "title": "Printer not working",
            "description": "Printer is not responding",
            "priority": "medium",
            "issue_type": "HARDWARE",
        },
        headers=employee_headers,
    )

    assert response.status_code == 201, response.text
    return response.json()


# Employee can view their own ticket history
def test_employee_get_own_ticket_history(
    client,
    employee_headers,
):
    ticket = create_ticket(client, employee_headers)

    response = client.get(
        f"/tickets/{ticket['id']}/history",
        headers=employee_headers,
    )

    assert response.status_code == 200

    history = response.json()

    assert len(history) == 1
    assert history[0]["ticket_id"] == ticket["id"]
    assert history[0]["old_status"] is None
    assert history[0]["new_status"] == "open"


# Admin can view ticket history
def test_admin_get_ticket_history(
    client,
    employee_headers,
    admin_headers,
):
    ticket = create_ticket(client, employee_headers)

    response = client.get(
        f"/tickets/{ticket['id']}/history",
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


# History is recorded after a status update
def test_history_after_status_update(
    client,
    employee_headers,
    admin_headers,
):
    ticket = create_ticket(client, employee_headers)
    ticket_id = ticket["id"]

    update_response = client.patch(
        f"/tickets/{ticket_id}/status",
        json={
            "status": "in_progress",
            "status_change_remark": "Work started",
        },
        headers=admin_headers,
    )

    assert update_response.status_code == 200

    response = client.get(
        f"/tickets/{ticket_id}/history",
        headers=admin_headers,
    )

    assert response.status_code == 200

    history = response.json()

    assert len(history) == 2
    assert history[0]["old_status"] is None
    assert history[0]["new_status"] == "open"
    assert history[1]["old_status"] == "open"
    assert history[1]["new_status"] == "in_progress"


# Employee cannot view another employee's ticket history
def test_employee_cannot_view_other_ticket_history(
    client,
    employee_headers,
    admin_headers,
):
    ticket = create_ticket(client, employee_headers)

    create_response = client.post(
        "/users",
        json={
            "username": "employee2",
            "email": "employee2@example.com",
            "password": "employee123",
            "role": "employee",
        },
        headers=admin_headers,
    )

    assert create_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        data={
            "username": "employee2",
            "password": "employee123",
        },
    )

    assert login_response.status_code == 200

    other_headers = {
        "Authorization": (f"Bearer {login_response.json()['access_token']}")
    }

    response = client.get(
        f"/tickets/{ticket['id']}/history",
        headers=other_headers,
    )

    assert response.status_code == 403


# Manager cannot access ticket history
def test_manager_cannot_access_history(
    client,
    employee_headers,
    manager_headers,
):
    ticket = create_ticket(client, employee_headers)

    response = client.get(
        f"/tickets/{ticket['id']}/history",
        headers=manager_headers,
    )

    assert response.status_code == 403


# Nonexistent ticket returns 404
def test_history_for_nonexistent_ticket(
    client,
    employee_headers,
):
    response = client.get(
        "/tickets/9999/history",
        headers=employee_headers,
    )

    assert response.status_code == 404


# Unauthenticated user cannot access ticket history
def test_history_without_token(client):
    response = client.get("/tickets/1/history")

    assert response.status_code == 401


# Invalid ticket ID returns 422
def test_history_invalid_ticket_id(
    client,
    employee_headers,
):
    response = client.get(
        "/tickets/invalid/history",
        headers=employee_headers,
    )

    assert response.status_code == 422


# Inactive employee cannot access ticket history
def test_inactive_employee_cannot_access_history(
    client,
    employee_headers,
    admin_headers,
):
    ticket = create_ticket(client, employee_headers)

    deactivate_response = client.delete(
        "/users/3",
        headers=admin_headers,
    )

    assert deactivate_response.status_code == 200

    response = client.get(
        f"/tickets/{ticket['id']}/history",
        headers=employee_headers,
    )

    assert response.status_code == 403
