from datetime import date, timedelta
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.salary import Salary
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


def test_admin_update_salary_inserts_history_rows(client: TestClient, db: Session) -> None:
    admin = _create_user(db, "ADM-001", "admin@example.com", UserRole.ADMIN)
    employee = _create_user(db, "EMP-001", "employee@example.com")
    token = _token(client, admin.email)

    first_response = client.post(
        f"/salary/{employee.id}/update",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "amount": "50000.00",
            "effective_date": date.today().isoformat(),
            "reason": "Initial salary",
        },
    )
    second_response = client.post(
        f"/salary/{employee.id}/update",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "amount": "60000.00",
            "effective_date": (date.today() + timedelta(days=30)).isoformat(),
            "reason": "Revision",
        },
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert db.query(Salary).count() == 2
    assert first_response.json()["id"] != second_response.json()["id"]
    assert second_response.json()["changed_by"] == admin.id


def test_admin_can_view_employee_salary_history(client: TestClient, db: Session) -> None:
    admin = _create_user(db, "ADM-001", "admin@example.com", UserRole.ADMIN)
    employee = _create_user(db, "EMP-001", "employee@example.com")
    token = _token(client, admin.email)
    today = date.today()

    client.post(
        f"/salary/{employee.id}/update",
        headers={"Authorization": f"Bearer {token}"},
        json={"amount": "50000.00", "effective_date": today.isoformat()},
    )
    client.post(
        f"/salary/{employee.id}/update",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "amount": "60000.00",
            "effective_date": (today + timedelta(days=30)).isoformat(),
        },
    )

    response = client.get(
        f"/salary/{employee.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert [row["amount"] for row in payload] == ["60000.00", "50000.00"]


def test_employee_can_view_own_salary_but_not_update(client: TestClient, db: Session) -> None:
    admin = _create_user(db, "ADM-001", "admin@example.com", UserRole.ADMIN)
    employee = _create_user(db, "EMP-001", "employee@example.com")
    admin_token = _token(client, admin.email)
    employee_token = _token(client, employee.email)

    client.post(
        f"/salary/{employee.id}/update",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"amount": "50000.00", "effective_date": date.today().isoformat()},
    )

    me_response = client.get(
        "/salary/me",
        headers={"Authorization": f"Bearer {employee_token}"},
    )
    update_response = client.post(
        f"/salary/{employee.id}/update",
        headers={"Authorization": f"Bearer {employee_token}"},
        json={"amount": "99999.00", "effective_date": date.today().isoformat()},
    )

    assert me_response.status_code == 200
    assert me_response.json()[0]["amount"] == "50000.00"
    assert update_response.status_code == 403


def test_employee_current_salary_is_latest_effective_row(
    client: TestClient,
    db: Session,
) -> None:
    admin = _create_user(db, "ADM-001", "admin@example.com", UserRole.ADMIN)
    employee = _create_user(db, "EMP-001", "employee@example.com")
    admin_token = _token(client, admin.email)
    employee_token = _token(client, employee.email)
    today = date.today()

    client.post(
        f"/salary/{employee.id}/update",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"amount": "50000.00", "effective_date": today.isoformat()},
    )
    client.post(
        f"/salary/{employee.id}/update",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "amount": "60000.00",
            "effective_date": (today + timedelta(days=1)).isoformat(),
        },
    )

    response = client.get(
        "/salary/me/current",
        headers={"Authorization": f"Bearer {employee_token}"},
    )

    assert response.status_code == 200
    assert Decimal(response.json()["amount"]) == Decimal("60000.00")


def test_salary_update_requires_existing_user(client: TestClient, db: Session) -> None:
    admin = _create_user(db, "ADM-001", "admin@example.com", UserRole.ADMIN)
    token = _token(client, admin.email)

    response = client.post(
        "/salary/999/update",
        headers={"Authorization": f"Bearer {token}"},
        json={"amount": "50000.00", "effective_date": date.today().isoformat()},
    )

    assert response.status_code == 404
