from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db, require_role
from app.models.user import User, UserRole
from app.schemas.salary import SalaryCreate, SalaryOut
from app.services.salary_service import (
    get_current_salary,
    list_salary_history,
    update_salary as update_salary_service,
)

router = APIRouter(prefix="/salary", tags=["salary"])


@router.get("/me", response_model=list[SalaryOut])
def my_salary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[SalaryOut]:
    return list_salary_history(db, current_user.id)


@router.get("/me/current", response_model=SalaryOut | None)
def my_current_salary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SalaryOut | None:
    return get_current_salary(db, current_user.id)


@router.get("/{user_id}", response_model=list[SalaryOut])
def user_salary(
    user_id: int,
    _: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
) -> list[SalaryOut]:
    return list_salary_history(db, user_id)


@router.post("/{user_id}/update", response_model=SalaryOut)
def update_salary(
    user_id: int,
    payload: SalaryCreate,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
) -> SalaryOut:
    return update_salary_service(db, user_id, current_user, payload)
