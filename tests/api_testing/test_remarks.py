# Helper function to create a ticket
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


# 1. Admin successfully adds a remark
def test_add_remark(client, employee_headers, admin_headers):
    ticket = create_ticket(client, employee_headers)

    response = client.post(
        f"/tickets/{ticket['id']}/remarks",
        json={"remark": "Investigating the reported issue."},
        headers=admin_headers,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["ticket_id"] == ticket["id"]
    assert data["remark"] == "Investigating the reported issue."
    assert data["user_id"] == 1
    assert data["admin_id"] == 1
    assert data["is_overdue"] is False


# 2. Employee cannot add a remark
def test_employee_cannot_add_remark(
    client,
    employee_headers,
):
    ticket = create_ticket(client, employee_headers)

    response = client.post(
        f"/tickets/{ticket['id']}/remarks",
        json={"remark": "Please check my ticket."},
        headers=employee_headers,
    )

    assert response.status_code == 403


# 3. Manager cannot add a remark
def test_manager_cannot_add_remark(
    client,
    employee_headers,
    manager_headers,
):
    ticket = create_ticket(client, employee_headers)

    response = client.post(
        f"/tickets/{ticket['id']}/remarks",
        json={"remark": "Checking the issue."},
        headers=manager_headers,
    )

    assert response.status_code == 403


# 4. Add remark to nonexistent ticket
def test_add_remark_to_nonexistent_ticket(
    client,
    admin_headers,
):
    response = client.post(
        "/tickets/9999/remarks",
        json={"remark": "Checking ticket."},
        headers=admin_headers,
    )

    assert response.status_code == 404


# 5. Add empty remark
def test_add_empty_remark(
    client,
    admin_headers,
):
    response = client.post(
        "/tickets/1/remarks",
        json={"remark": ""},
        headers=admin_headers,
    )

    assert response.status_code == 422


# 6. Add remark without authentication
def test_add_remark_without_token(client):
    response = client.post(
        "/tickets/1/remarks",
        json={"remark": "Checking ticket."},
    )

    assert response.status_code == 401


# 7. Admin retrieves ticket remarks
def test_admin_get_remarks(
    client,
    employee_headers,
    admin_headers,
):
    ticket = create_ticket(client, employee_headers)

    client.post(
        f"/tickets/{ticket['id']}/remarks",
        json={"remark": "Issue is being investigated."},
        headers=admin_headers,
    )

    response = client.get(
        f"/tickets/{ticket['id']}/remarks",
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["remark"] == "Issue is being investigated."


# 8. Employee retrieves own ticket remarks
def test_employee_get_own_remarks(
    client,
    employee_headers,
    admin_headers,
):
    ticket = create_ticket(client, employee_headers)

    client.post(
        f"/tickets/{ticket['id']}/remarks",
        json={"remark": "Issue is being investigated."},
        headers=admin_headers,
    )

    response = client.get(
        f"/tickets/{ticket['id']}/remarks",
        headers=employee_headers,
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


# 9. Manager retrieves ticket remarks
def test_manager_get_remarks(
    client,
    employee_headers,
    manager_headers,
    admin_headers,
):
    ticket = create_ticket(client, employee_headers)

    client.post(
        f"/tickets/{ticket['id']}/remarks",
        json={"remark": "Issue is being investigated."},
        headers=admin_headers,
    )

    response = client.get(
        f"/tickets/{ticket['id']}/remarks",
        headers=manager_headers,
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


# 10. Employee cannot view another employee's remarks
def test_employee_cannot_view_other_remarks(
    client,
    employee_headers,
    admin_headers,
):
    ticket = create_ticket(client, employee_headers)

    # Create another employee
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

    # Login as the second employee
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
        f"/tickets/{ticket['id']}/remarks",
        headers=other_headers,
    )

    assert response.status_code == 403


# 11. Get remarks for nonexistent ticket
def test_get_remarks_for_nonexistent_ticket(
    client,
    admin_headers,
):
    response = client.get(
        "/tickets/9999/remarks",
        headers=admin_headers,
    )

    assert response.status_code == 404


# 12. Get remarks without authentication
def test_get_remarks_without_token(client):
    response = client.get("/tickets/1/remarks")

    assert response.status_code == 401
