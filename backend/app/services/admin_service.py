from datetime import datetime, timezone

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from app.models.attendance import Attendance, AttendanceStatus
from app.models.leave import LeaveRequest, LeaveStatus
from app.models.profile import Profile
from app.models.user import User, UserRole
from app.schemas.admin import EmployeeListItem


def get_admin_stats(db: Session) -> dict[str, int]:
    today = datetime.now(timezone.utc).date()

    headcount = db.scalar(
        select(func.count()).select_from(User).where(
            User.role == UserRole.EMPLOYEE,
            User.is_active.is_(True),
        ),
    ) or 0

    pending_leaves = db.scalar(
        select(func.count()).select_from(LeaveRequest).where(
            LeaveRequest.status == LeaveStatus.PENDING,
        ),
    ) or 0

    attended_today = db.scalar(
        select(func.count())
        .select_from(Attendance)
        .join(User, User.id == Attendance.user_id)
        .where(
            User.role == UserRole.EMPLOYEE,
            User.is_active.is_(True),
            Attendance.date == today,
            Attendance.status.in_(
                [
                    AttendanceStatus.PRESENT,
                    AttendanceStatus.HALF_DAY,
                    AttendanceStatus.LATE,
                    AttendanceStatus.ON_LEAVE,
                ],
            ),
        ),
    ) or 0

    attendance_percentage_today = round((attended_today / headcount) * 100) if headcount else 0

    return {
        "headcount": headcount,
        "pending_leaves": pending_leaves,
        "attendance_percentage_today": attendance_percentage_today,
    }


def list_employees(
    db: Session,
    search: str | None = None,
    department: str | None = None,
    is_active: bool | None = None,
) -> list[EmployeeListItem]:
    query: Select[tuple[User, Profile]] = (
        select(User, Profile)
        .join(Profile, Profile.user_id == User.id, isouter=True)
        .where(User.role == UserRole.EMPLOYEE)
    )

    if search:
        pattern = f"%{search}%"
        query = query.where(
            or_(
                User.email.ilike(pattern),
                User.employee_id.ilike(pattern),
                Profile.department.ilike(pattern),
                Profile.designation.ilike(pattern),
            ),
        )
    if department:
        query = query.where(Profile.department == department)
    if is_active is not None:
        query = query.where(User.is_active.is_(is_active))

    query = query.order_by(User.created_at.desc(), User.id.desc())

    employees: list[EmployeeListItem] = []
    for user, profile in db.execute(query).all():
        employees.append(
            EmployeeListItem(
                id=user.id,
                employee_id=user.employee_id,
                email=user.email,
                role=user.role,
                is_active=user.is_active,
                created_at=user.created_at,
                department=profile.department if profile else None,
                designation=profile.designation if profile else None,
            ),
        )

    return employees
