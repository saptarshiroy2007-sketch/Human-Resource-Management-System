from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.attendance import Attendance, AttendanceStatus
from app.models.user import User, UserRole
from app.schemas.leave import LeaveCreate
from app.schemas.profile import ProfileAdminUpdate
from app.schemas.user import UserCreate
from app.services.auth_service import create_user
from app.services.leave_service import apply_leave
from app.services.profile_service import update_admin_profile


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


def test_admin_stats_counts_headcount_pending_leaves_and_attendance(
    client: TestClient,
    db: Session,
) -> None:
    admin = _create_user(db, "ADM-001", "admin@example.com", UserRole.ADMIN)
    employee_one = _create_user(db, "EMP-001", "one@example.com")
    employee_two = _create_user(db, "EMP-002", "two@example.com")
    inactive_employee = _create_user(db, "EMP-003", "inactive@example.com")
    inactive_employee.is_active = False
    db.add(
        Attendance(
            user_id=employee_one.id,
            date=date.today(),
            status=AttendanceStatus.PRESENT,
        ),
    )
    apply_leave(
        db,
        employee_two,
        LeaveCreate(
            leave_type="paid",
            start_date=date.today(),
            end_date=date.today(),
            reason="Family commitment",
        ),
    )
    db.commit()
    token = _token(client, admin.email)

    response = client.get("/admin/stats", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json() == {
        "headcount": 2,
        "pending_leaves": 1,
        "attendance_percentage_today": 50,
    }


def test_admin_can_list_search_and_filter_employees(
    client: TestClient,
    db: Session,
) -> None:
    admin = _create_user(db, "ADM-001", "admin@example.com", UserRole.ADMIN)
    employee_one = _create_user(db, "EMP-001", "one@example.com")
    employee_two = _create_user(db, "EMP-002", "two@example.com")
    update_admin_profile(
        db,
        employee_one.id,
        ProfileAdminUpdate(department="Engineering", designation="Backend Developer"),
    )
    update_admin_profile(
        db,
        employee_two.id,
        ProfileAdminUpdate(department="Finance", designation="Payroll Analyst"),
    )
    token = _token(client, admin.email)

    all_response = client.get("/admin/employees", headers={"Authorization": f"Bearer {token}"})
    search_response = client.get(
        "/admin/employees?search=payroll",
        headers={"Authorization": f"Bearer {token}"},
    )
    department_response = client.get(
        "/admin/employees?department=Engineering",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert all_response.status_code == 200
    assert len(all_response.json()) == 2
    assert search_response.status_code == 200
    assert [row["email"] for row in search_response.json()] == ["two@example.com"]
    assert department_response.status_code == 200
    assert [row["email"] for row in department_response.json()] == ["one@example.com"]


def test_employee_cannot_access_admin_endpoints(client: TestClient, db: Session) -> None:
    employee = _create_user(db, "EMP-001", "employee@example.com")
    token = _token(client, employee.email)

    stats_response = client.get("/admin/stats", headers={"Authorization": f"Bearer {token}"})
    employees_response = client.get("/admin/employees", headers={"Authorization": f"Bearer {token}"})

    assert stats_response.status_code == 403
    assert employees_response.status_code == 403
