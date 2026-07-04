from fastapi import HTTPException, status
from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.salary import Salary
from app.models.user import User
from app.schemas.salary import SalaryCreate


def list_salary_history(db: Session, user_id: int) -> list[Salary]:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    query: Select[tuple[Salary]] = (
        select(Salary)
        .where(Salary.user_id == user_id)
        .order_by(Salary.effective_date.desc(), Salary.created_at.desc(), Salary.id.desc())
    )
    return list(db.scalars(query))


def get_current_salary(db: Session, user_id: int) -> Salary | None:
    history = list_salary_history(db, user_id)
    return history[0] if history else None


def update_salary(
    db: Session,
    user_id: int,
    changed_by: User,
    payload: SalaryCreate,
) -> Salary:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    salary = Salary(
        user_id=user_id,
        amount=payload.amount,
        effective_date=payload.effective_date,
        changed_by=changed_by.id,
        reason=payload.reason,
    )
    db.add(salary)
    db.commit()
    db.refresh(salary)
    return salary
