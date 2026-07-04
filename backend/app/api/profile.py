from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db, require_role
from app.models.user import User, UserRole
from app.schemas.profile import ProfileAdminUpdate, ProfileEmployeeUpdate, ProfileOut
from app.services.profile_service import (
    get_profile,
    update_admin_profile,
    update_employee_profile,
)

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/me", response_model=ProfileOut)
def my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProfileOut:
    return get_profile(db, current_user.id)


@router.patch("/me", response_model=ProfileOut)
def update_my_profile(
    payload: ProfileEmployeeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProfileOut:
    return update_employee_profile(db, current_user.id, payload)


@router.get("/{user_id}", response_model=ProfileOut)
def user_profile(
    user_id: int,
    _: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
) -> ProfileOut:
    return get_profile(db, user_id)


@router.patch("/{user_id}", response_model=ProfileOut)
def update_user_profile(
    user_id: int,
    payload: ProfileAdminUpdate,
    _: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
) -> ProfileOut:
    return update_admin_profile(db, user_id, payload)
