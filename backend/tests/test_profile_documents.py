from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.document import Document
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


def test_employee_can_view_and_update_limited_profile(
    client: TestClient,
    db: Session,
) -> None:
    employee = _create_user(db, "EMP-001", "employee@example.com")
    token = _token(client, employee.email)

    update_response = client.patch(
        "/profile/me",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "phone": "555-0101",
            "address": "42 Payroll Street",
            "department": "Finance",
        },
    )

    assert update_response.status_code == 200
    payload = update_response.json()
    assert payload["phone"] == "555-0101"
    assert payload["address"] == "42 Payroll Street"
    assert payload["department"] is None

    get_response = client.get("/profile/me", headers={"Authorization": f"Bearer {token}"})
    assert get_response.status_code == 200
    assert get_response.json()["user_id"] == employee.id


def test_admin_can_update_full_employee_profile(client: TestClient, db: Session) -> None:
    admin = _create_user(db, "ADM-001", "admin@example.com", UserRole.ADMIN)
    employee = _create_user(db, "EMP-001", "employee@example.com")
    token = _token(client, admin.email)

    response = client.patch(
        f"/profile/{employee.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "phone": "555-0101",
            "department": "Engineering",
            "designation": "Backend Developer",
            "joining_date": "2026-07-04",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["department"] == "Engineering"
    assert payload["designation"] == "Backend Developer"
    assert payload["joining_date"] == "2026-07-04"


def test_employee_cannot_view_other_profile(client: TestClient, db: Session) -> None:
    employee = _create_user(db, "EMP-001", "employee@example.com")
    other = _create_user(db, "EMP-002", "other@example.com")
    token = _token(client, employee.email)

    response = client.get(
        f"/profile/{other.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_employee_can_upload_list_and_delete_document(
    client: TestClient,
    db: Session,
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(settings, "file_storage_path", str(tmp_path))
    employee = _create_user(db, "EMP-001", "employee@example.com")
    token = _token(client, employee.email)

    upload_response = client.post(
        "/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        data={"doc_type": "id_proof"},
        files={"file": ("id.txt", b"employee-id", "text/plain")},
    )

    assert upload_response.status_code == 201
    payload = upload_response.json()
    stored_path = Path(payload["file_url"])
    assert stored_path.exists()
    assert stored_path.read_bytes() == b"employee-id"

    list_response = client.get(
        "/documents/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert list_response.json()[0]["doc_type"] == "id_proof"

    delete_response = client.delete(
        f"/documents/{payload['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert delete_response.status_code == 204
    assert not stored_path.exists()
    assert db.query(Document).count() == 0


def test_employee_cannot_delete_other_users_document(
    client: TestClient,
    db: Session,
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(settings, "file_storage_path", str(tmp_path))
    owner = _create_user(db, "EMP-001", "owner@example.com")
    other = _create_user(db, "EMP-002", "other@example.com")
    owner_token = _token(client, owner.email)
    other_token = _token(client, other.email)

    upload_response = client.post(
        "/documents/upload",
        headers={"Authorization": f"Bearer {owner_token}"},
        data={"doc_type": "contract"},
        files={"file": ("contract.txt", b"contract", "text/plain")},
    )
    document_id = upload_response.json()["id"]
    stored_path = Path(upload_response.json()["file_url"])

    delete_response = client.delete(
        f"/documents/{document_id}",
        headers={"Authorization": f"Bearer {other_token}"},
    )

    assert delete_response.status_code == 403
    assert stored_path.exists()
    assert db.query(Document).count() == 1


def test_admin_can_delete_employee_document(
    client: TestClient,
    db: Session,
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(settings, "file_storage_path", str(tmp_path))
    admin = _create_user(db, "ADM-001", "admin@example.com", UserRole.ADMIN)
    employee = _create_user(db, "EMP-001", "employee@example.com")
    admin_token = _token(client, admin.email)
    employee_token = _token(client, employee.email)

    upload_response = client.post(
        "/documents/upload",
        headers={"Authorization": f"Bearer {employee_token}"},
        data={"doc_type": "contract"},
        files={"file": ("contract.txt", b"contract", "text/plain")},
    )
    document_id = upload_response.json()["id"]
    stored_path = Path(upload_response.json()["file_url"])

    delete_response = client.delete(
        f"/documents/{document_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert delete_response.status_code == 204
    assert not stored_path.exists()
    assert db.query(Document).count() == 0
