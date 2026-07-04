from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Salary(Base):
    __tablename__ = "salaries"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    effective_date: Mapped[date] = mapped_column(Date, index=True)
    changed_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(
        foreign_keys=[user_id],
        back_populates="salary_records",
    )
    changed_by_user: Mapped["User"] = relationship(
        foreign_keys=[changed_by],
        back_populates="salary_changes",
    )
