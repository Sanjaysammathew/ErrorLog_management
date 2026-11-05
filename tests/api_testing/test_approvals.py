


# HELPER FUNCTION


def create_pending_approval(client, employee_headers):
    # Create a ticket that requires manager approval
    response = client.post(
        "/tickets",
        json={
            "title": "Hardware replacement required",
            "description": "Laptop motherboard replacement needed",
            "priority": "high",
            "issue_type": "HARDWARE",
        },
        headers=employee_headers,
    )

    assert response.status_code == 201
    assert response.json()["requires_approval"] is True

    assert response.json()["status"] == "pending_approval"

    return response.json()


# 1. GET PENDING APPROVALS


def test_get_pending_approvals(
    client,
    employee_headers,
    manager_headers,
    mock_email_service,
):
    create_pending_approval(client, employee_headers)

    response = client.get(
        "/approvals/pending-approvals",
        headers=manager_headers,
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["status"] == "pending"


# 2. GET EMPTY PENDING APPROVALS


def test_get_empty_pending_approvals(client, manager_headers):
    response = client.get(
        "/approvals/pending-approvals",
        headers=manager_headers,
    )

    assert response.status_code == 200
    assert response.json() == []


# 3. GET APPROVAL BY ID


def test_get_approval_by_id(
    client,
    employee_headers,
    manager_headers,
):
    create_pending_approval(client, employee_headers)

    pending_response = client.get(
        "/approvals/pending-approvals",
        headers=manager_headers,
    )

    approval_id = pending_response.json()[0]["id"]

    response = client.get(
        f"/approvals/{approval_id}",
        headers=manager_headers,
    )

    assert response.status_code == 200
    assert response.json()["id"] == approval_id
    assert response.json()["status"] == "pending"


# 4. GET NONEXISTENT APPROVAL


def test_get_nonexistent_approval(client, manager_headers):
    response = client.get(
        "/approvals/9999",
        headers=manager_headers,
    )

    assert response.status_code == 404


# 5. APPROVE TICKET


def test_approve_ticket(
    client,
    employee_headers,
    manager_headers,
    mock_email_service,
):
    create_pending_approval(client, employee_headers)

    pending_response = client.get(
        "/approvals/pending-approvals",
        headers=manager_headers,
    )

    approval_id = pending_response.json()[0]["id"]

    response = client.patch(
        f"/approvals/{approval_id}/approve",
        json={
            "decision_reason": "Approved for hardware replacement",
        },
        headers=manager_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "approved"
    assert data["decision_reason"] == "Approved for hardware replacement"
    assert data["approved_at"] is not None
    assert data["ticket"]["status"] == "open"

    mock_email_service.send_approval_decision.assert_awaited_once()


# 6. APPROVE WITHOUT REASON


def test_approve_without_reason(
    client,
    employee_headers,
    manager_headers,
):
    create_pending_approval(client, employee_headers)

    pending_response = client.get(
        "/approvals/pending-approvals",
        headers=manager_headers,
    )

    approval_id = pending_response.json()[0]["id"]

    response = client.patch(
        f"/approvals/{approval_id}/approve",
        headers=manager_headers,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "approved"
    assert response.json()["decision_reason"] is None


# 7. REJECT TICKET


def test_reject_ticket(
    client,
    employee_headers,
    manager_headers,
    mock_email_service,
):
    create_pending_approval(client, employee_headers)

    pending_response = client.get(
        "/approvals/pending-approvals",
        headers=manager_headers,
    )

    approval_id = pending_response.json()[0]["id"]

    response = client.patch(
        f"/approvals/{approval_id}/reject",
        json={
            "decision_reason": "Replacement is not necessary",
        },
        headers=manager_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "rejected"
    assert data["decision_reason"] == "Replacement is not necessary"
    assert data["approved_at"] is not None
    assert data["ticket"]["status"] == "rejected"

    mock_email_service.send_approval_decision.assert_awaited_once()


# 8. APPROVE ALREADY DECIDED APPROVAL


def test_approve_already_decided(
    client,
    employee_headers,
    manager_headers,
):
    create_pending_approval(client, employee_headers)

    pending_response = client.get(
        "/approvals/pending-approvals",
        headers=manager_headers,
    )

    approval_id = pending_response.json()[0]["id"]

    first_response = client.patch(
        f"/approvals/{approval_id}/approve",
        headers=manager_headers,
    )

    assert first_response.status_code == 200

    second_response = client.patch(
        f"/approvals/{approval_id}/approve",
        headers=manager_headers,
    )

    assert second_response.status_code == 409


# 9. ADMIN CANNOT ACCESS APPROVALS


def test_admin_cannot_get_pending_approvals(
    client,
    admin_headers,
):
    response = client.get(
        "/approvals/pending-approvals",
        headers=admin_headers,
    )

    assert response.status_code == 403


# 10. EMPLOYEE CANNOT ACCESS APPROVALS


def test_employee_cannot_get_pending_approvals(
    client,
    employee_headers,
):
    response = client.get(
        "/approvals/pending-approvals",
        headers=employee_headers,
    )

    assert response.status_code == 403


# 11. UNAUTHENTICATED ACCESS


def test_get_pending_approvals_without_token(client):
    response = client.get("/approvals/pending-approvals")

    assert response.status_code == 401


# 12. MANAGER CANNOT APPROVE NONEXISTENT APPROVAL


def test_approve_nonexistent_approval(client, manager_headers):
    response = client.patch(
        "/approvals/9999/approve",
        json={
            "decision_reason": "Approved",
        },
        headers=manager_headers,
    )

    assert response.status_code == 404
