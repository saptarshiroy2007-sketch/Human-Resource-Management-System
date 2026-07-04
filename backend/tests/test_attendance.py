from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

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


def test_employee_can_check_in_and_check_out(client: TestClient, db: Session) -> None:
    employee = _create_user(db, "EMP-001", "employee@example.com")
    token = _token(client, employee.email)

    check_in_response = client.post(
        "/attendance/check-in",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert check_in_response.status_code == 200
    check_in_payload = check_in_response.json()
    assert check_in_payload["user_id"] == employee.id
    assert check_in_payload["status"] == "present"
    assert check_in_payload["check_in"] is not None
    assert check_in_payload["check_out"] is None

    check_out_response = client.post(
        "/attendance/check-out",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert check_out_response.status_code == 200
    assert check_out_response.json()["check_out"] is not None


def test_double_check_in_is_rejected(client: TestClient, db: Session) -> None:
    employee = _create_user(db, "EMP-001", "employee@example.com")
    token = _token(client, employee.email)

    first_response = client.post(
        "/attendance/check-in",
        headers={"Authorization": f"Bearer {token}"},
    )
    second_response = client.post(
        "/attendance/check-in",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 409


def test_check_out_requires_check_in(client: TestClient, db: Session) -> None:
    employee = _create_user(db, "EMP-001", "employee@example.com")
    token = _token(client, employee.email)

    response = client.post(
        "/attendance/check-out",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400


def test_employee_can_view_own_attendance(client: TestClient, db: Session) -> None:
    employee = _create_user(db, "EMP-001", "employee@example.com")
    token = _token(client, employee.email)
    client.post("/attendance/check-in", headers={"Authorization": f"Bearer {token}"})

    response = client.get(
        "/attendance/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["user_id"] == employee.id


def test_admin_can_view_employee_attendance(client: TestClient, db: Session) -> None:
    admin = _create_user(db, "ADM-001", "admin@example.com", UserRole.ADMIN)
    employee = _create_user(db, "EMP-001", "employee@example.com")
    employee_token = _token(client, employee.email)
    admin_token = _token(client, admin.email)
    client.post("/attendance/check-in", headers={"Authorization": f"Bearer {employee_token}"})

    response = client.get(
        f"/attendance/{employee.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["user_id"] == employee.id


def test_employee_cannot_view_all_attendance(client: TestClient, db: Session) -> None:
    employee = _create_user(db, "EMP-001", "employee@example.com")
    token = _token(client, employee.email)

    response = client.get(
        "/attendance/all",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
