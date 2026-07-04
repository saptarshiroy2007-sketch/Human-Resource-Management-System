from datetime import date, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.attendance import Attendance, AttendanceStatus
from app.models.user import User, UserRole
from app.schemas.user import UserCreate
from app.services.auth_service import create_user


def _create_user(
    db: Session,
    employee_id: str,
    email: str,
    role: UserRole = UserRole.EMPLOYEE,
) -> User:
    return create_user(
        db,
        UserCreate(
            employee_id=employee_id,
            email=email,
            password="secret123",
            role=role,
        ),
    )


def _token(client: TestClient, email: str) -> str:
    response = client.post(
        "/auth/login",
        data={"username": email, "password": "secret123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def _leave_payload(start_date: date | None = None, end_date: date | None = None) -> dict[str, str]:
    start = start_date or date.today()
    end = end_date or start
    return {
        "leave_type": "paid",
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "reason": "Family commitment",
    }


def test_employee_can_apply_and_view_own_leave(client: TestClient, db: Session) -> None:
    employee = _create_user(db, "EMP-001", "employee@example.com")
    token = _token(client, employee.email)

    apply_response = client.post(
        "/leave/apply",
        headers={"Authorization": f"Bearer {token}"},
        json=_leave_payload(),
    )
    assert apply_response.status_code == 201
    assert apply_response.json()["status"] == "pending"

    list_response = client.get(
        "/leave/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert list_response.json()[0]["user_id"] == employee.id


def test_employee_can_cancel_pending_leave(client: TestClient, db: Session) -> None:
    employee = _create_user(db, "EMP-001", "employee@example.com")
    token = _token(client, employee.email)
    apply_response = client.post(
        "/leave/apply",
        headers={"Authorization": f"Bearer {token}"},
        json=_leave_payload(),
    )
    leave_id = apply_response.json()["id"]

    cancel_response = client.post(
        f"/leave/{leave_id}/cancel",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert cancel_response.status_code == 204

    list_response = client.get(
        "/leave/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert list_response.json() == []


def test_admin_can_approve_leave_and_sync_attendance(client: TestClient, db: Session) -> None:
    admin = _create_user(db, "ADM-001", "admin@example.com", UserRole.ADMIN)
    employee = _create_user(db, "EMP-001", "employee@example.com")
    admin_token = _token(client, admin.email)
    employee_token = _token(client, employee.email)
    start_date = date.today() + timedelta(days=1)
    end_date = start_date + timedelta(days=1)

    apply_response = client.post(
        "/leave/apply",
        headers={"Authorization": f"Bearer {employee_token}"},
        json=_leave_payload(start_date, end_date),
    )
    leave_id = apply_response.json()["id"]

    approve_response = client.post(
        f"/leave/{leave_id}/approve",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"admin_comment": "Approved"},
    )

    assert approve_response.status_code == 200
    payload = approve_response.json()
    assert payload["status"] == "approved"
    assert payload["reviewed_by"] == admin.id

    attendance_response = client.get(
        f"/attendance/{employee.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    attendance_payload = attendance_response.json()
    assert len(attendance_payload) == 2
    assert {row["status"] for row in attendance_payload} == {"on_leave"}


def test_admin_can_reject_leave_without_attendance_sync(client: TestClient, db: Session) -> None:
    admin = _create_user(db, "ADM-001", "admin@example.com", UserRole.ADMIN)
    employee = _create_user(db, "EMP-001", "employee@example.com")
    admin_token = _token(client, admin.email)
    employee_token = _token(client, employee.email)

    apply_response = client.post(
        "/leave/apply",
        headers={"Authorization": f"Bearer {employee_token}"},
        json=_leave_payload(),
    )
    leave_id = apply_response.json()["id"]

    reject_response = client.post(
        f"/leave/{leave_id}/reject",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"admin_comment": "Not enough balance"},
    )

    assert reject_response.status_code == 200
    assert reject_response.json()["status"] == "rejected"
    assert db.query(Attendance).count() == 0


def test_employee_cannot_view_all_leaves(client: TestClient, db: Session) -> None:
    employee = _create_user(db, "EMP-001", "employee@example.com")
    token = _token(client, employee.email)

    response = client.get(
        "/leave/all",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_approve_leave_conflicts_with_existing_attendance_activity(
    client: TestClient,
    db: Session,
) -> None:
    admin = _create_user(db, "ADM-001", "admin@example.com", UserRole.ADMIN)
    employee = _create_user(db, "EMP-001", "employee@example.com")
    admin_token = _token(client, admin.email)
    employee_token = _token(client, employee.email)
    leave_date = date.today()

    check_in_response = client.post(
        "/attendance/check-in",
        headers={"Authorization": f"Bearer {employee_token}"},
    )
    assert check_in_response.status_code == 200

    apply_response = client.post(
        "/leave/apply",
        headers={"Authorization": f"Bearer {employee_token}"},
        json=_leave_payload(leave_date, leave_date),
    )
    leave_id = apply_response.json()["id"]

    approve_response = client.post(
        f"/leave/{leave_id}/approve",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={},
    )

    assert approve_response.status_code == 409
    attendance = db.query(Attendance).one()
    assert attendance.status == AttendanceStatus.PRESENT
