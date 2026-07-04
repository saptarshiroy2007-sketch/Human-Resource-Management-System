from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db, require_role
from app.models.user import User, UserRole
from app.schemas.attendance import AttendanceOut
from app.services.attendance_service import (
    check_in as check_in_service,
    check_out as check_out_service,
    list_attendance,
    list_user_attendance,
)

router = APIRouter(prefix="/attendance", tags=["attendance"])


@router.post("/check-in", response_model=AttendanceOut)
def check_in(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AttendanceOut:
    return check_in_service(db, current_user)


@router.post("/check-out", response_model=AttendanceOut)
def check_out(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AttendanceOut:
    return check_out_service(db, current_user)


@router.get("/me", response_model=list[AttendanceOut])
def my_attendance(
    start_date: date | None = None,
    end_date: date | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[AttendanceOut]:
    return list_user_attendance(db, current_user.id, start_date, end_date)


@router.get("/all", response_model=list[AttendanceOut])
def all_attendance(
    start_date: date | None = None,
    end_date: date | None = None,
    _: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
) -> list[AttendanceOut]:
    return list_attendance(db, start_date=start_date, end_date=end_date)


@router.get("/{user_id}", response_model=list[AttendanceOut])
def user_attendance(
    user_id: int,
    start_date: date | None = None,
    end_date: date | None = None,
    _: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
) -> list[AttendanceOut]:
    return list_user_attendance(db, user_id, start_date, end_date)
