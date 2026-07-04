from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db, require_role
from app.models.leave import LeaveStatus
from app.models.user import User, UserRole
from app.schemas.leave import LeaveCreate, LeaveOut, LeaveReview
from app.services.leave_service import (
    apply_leave as apply_leave_service,
    approve_leave as approve_leave_service,
    cancel_leave as cancel_leave_service,
    list_leaves,
    reject_leave as reject_leave_service,
)

router = APIRouter(prefix="/leave", tags=["leave"])


@router.post("/apply", response_model=LeaveOut, status_code=status.HTTP_201_CREATED)
def apply_leave(
    payload: LeaveCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> LeaveOut:
    return apply_leave_service(db, current_user, payload)


@router.get("/me", response_model=list[LeaveOut])
def my_leaves(
    leave_status: LeaveStatus | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[LeaveOut]:
    return list_leaves(db, user_id=current_user.id, leave_status=leave_status)


@router.post("/{leave_id}/cancel", status_code=status.HTTP_204_NO_CONTENT)
def cancel_leave(
    leave_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    cancel_leave_service(db, current_user, leave_id)
    return None


@router.get("/all", response_model=list[LeaveOut])
def all_leaves(
    leave_status: LeaveStatus | None = None,
    _: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
) -> list[LeaveOut]:
    return list_leaves(db, leave_status=leave_status)


@router.post("/{leave_id}/approve", response_model=LeaveOut)
def approve_leave(
    leave_id: int,
    payload: LeaveReview,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
) -> LeaveOut:
    return approve_leave_service(db, leave_id, current_user, payload.admin_comment)


@router.post("/{leave_id}/reject", response_model=LeaveOut)
def reject_leave(
    leave_id: int,
    payload: LeaveReview,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
) -> LeaveOut:
    return reject_leave_service(db, leave_id, current_user, payload.admin_comment)
