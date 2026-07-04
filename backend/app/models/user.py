import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    EMPLOYEE = "employee"


def enum_values(enum_class: type[enum.Enum]) -> list[str]:
    return [member.value for member in enum_class]


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    employee_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, values_callable=enum_values),
        default=UserRole.EMPLOYEE,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    profile: Mapped["Profile"] = relationship(back_populates="user", uselist=False)
    attendance_records: Mapped[list["Attendance"]] = relationship(back_populates="user")
    leave_requests: Mapped[list["LeaveRequest"]] = relationship(
        foreign_keys="LeaveRequest.user_id",
        back_populates="user",
    )
    reviewed_leave_requests: Mapped[list["LeaveRequest"]] = relationship(
        foreign_keys="LeaveRequest.reviewed_by",
        back_populates="reviewer",
    )
    salary_records: Mapped[list["Salary"]] = relationship(
        foreign_keys="Salary.user_id",
        back_populates="user",
    )
    salary_changes: Mapped[list["Salary"]] = relationship(
        foreign_keys="Salary.changed_by",
        back_populates="changed_by_user",
    )
    documents: Mapped[list["Document"]] = relationship(back_populates="user")
