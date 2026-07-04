import enum
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class LeaveType(str, enum.Enum):
    PAID = "paid"
    SICK = "sick"
    UNPAID = "unpaid"


class LeaveStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


def enum_values(enum_class: type[enum.Enum]) -> list[str]:
    return [member.value for member in enum_class]


class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    leave_type: Mapped[LeaveType] = mapped_column(
        Enum(LeaveType, values_callable=enum_values),
    )
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    reason: Mapped[str] = mapped_column(Text)
    status: Mapped[LeaveStatus] = mapped_column(
        Enum(LeaveStatus, values_callable=enum_values),
        default=LeaveStatus.PENDING,
    )
    admin_comment: Mapped[str | None] = mapped_column(Text)
    reviewed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship(
        foreign_keys=[user_id],
        back_populates="leave_requests",
    )
    reviewer: Mapped["User | None"] = relationship(
        foreign_keys=[reviewed_by],
        back_populates="reviewed_leave_requests",
    )
