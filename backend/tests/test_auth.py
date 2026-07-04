from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import UserRole
from app.schemas.user import UserCreate
from app.services.auth_service import create_user
from scripts.bootstrap_admin import bootstrap_admin


def test_admin_can_create_employee(client: TestClient, db: Session) -> None:
    admin = create_user(
        db,
        UserCreate(
            employee_id="ADM-001",
            email="admin@example.com",
            password="secret123",
            role=UserRole.ADMIN,
        ),
    )

    login_response = client.post(
        "/auth/login",
        data={"username": admin.email, "password": "secret123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    signup_response = client.post(
        "/auth/signup",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "employee_id": "EMP-001",
            "email": "employee@example.com",
            "password": "secret123",
            "role": "employee",
        },
    )

    assert signup_response.status_code == 201
    payload = signup_response.json()
    assert payload["email"] == "employee@example.com"
    assert payload["role"] == "employee"
    assert "password_hash" not in payload


def test_employee_cannot_create_employee(client: TestClient, db: Session) -> None:
    employee = create_user(
        db,
        UserCreate(
            employee_id="EMP-001",
            email="employee@example.com",
            password="secret123",
        ),
    )
    login_response = client.post(
        "/auth/login",
        data={"username": employee.email, "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    signup_response = client.post(
        "/auth/signup",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "employee_id": "EMP-002",
            "email": "employee2@example.com",
            "password": "secret123",
            "role": "employee",
        },
    )

    assert signup_response.status_code == 403


def test_me_returns_authenticated_user(client: TestClient, db: Session) -> None:
    user = create_user(
        db,
        UserCreate(
            employee_id="ADM-001",
            email="admin@example.com",
            password="secret123",
            role=UserRole.ADMIN,
        ),
    )
    login_response = client.post(
        "/auth/login",
        data={"username": user.email, "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    me_response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert me_response.status_code == 200
    assert me_response.json()["email"] == user.email


def test_login_rejects_bad_password(client: TestClient, db: Session) -> None:
    create_user(
        db,
        UserCreate(
            employee_id="ADM-001",
            email="admin@example.com",
            password="secret123",
            role=UserRole.ADMIN,
        ),
    )

    response = client.post(
        "/auth/login",
        data={"username": "admin@example.com", "password": "wrong"},
    )

    assert response.status_code == 401


def test_bootstrap_admin_creates_only_first_admin(db: Session) -> None:
    first_admin = bootstrap_admin("ADM-001", "admin@example.com", "secret123", db)
    assert first_admin.role == UserRole.ADMIN

    try:
        bootstrap_admin("ADM-002", "admin2@example.com", "secret123", db)
    except RuntimeError as exc:
        assert "admin already exists" in str(exc)
    else:
        raise AssertionError("Expected second admin bootstrap to fail")
