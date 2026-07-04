from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, require_role
from app.models.user import User, UserRole
from app.schemas.admin import AdminStatsOut, EmployeeListItem
from app.services.admin_service import get_admin_stats, list_employees


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats", response_model=AdminStatsOut)
def stats(
    _: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
) -> AdminStatsOut:
    return get_admin_stats(db)


@router.get("/employees", response_model=list[EmployeeListItem])
def employees(
    search: str | None = None,
    department: str | None = None,
    is_active: bool | None = None,
    _: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
) -> list[EmployeeListItem]:
    return list_employees(db, search=search, department=department, is_active=is_active)
