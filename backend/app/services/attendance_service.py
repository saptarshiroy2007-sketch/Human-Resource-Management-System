from datetime import date, datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.attendance import Attendance, AttendanceStatus
from app.models.user import User


def _today() -> date:
    return datetime.now(timezone.utc).date()


def _now() -> datetime:
    return datetime.now(timezone.utc)


def check_in(db: Session, user: User) -> Attendance:
    today = _today()
    attendance = db.scalar(
        select(Attendance).where(
            Attendance.user_id == user.id,
            Attendance.date == today,
        ),
    )

    if attendance is not None:
        if attendance.status == AttendanceStatus.ON_LEAVE:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot check in while marked on leave",
            )
        if attendance.check_in is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Already checked in today",
            )

        attendance.check_in = _now()
        attendance.status = AttendanceStatus.PRESENT
    else:
        attendance = Attendance(
            user_id=user.id,
            date=today,
            check_in=_now(),
            status=AttendanceStatus.PRESENT,
        )
        db.add(attendance)

    db.commit()
    db.refresh(attendance)
    return attendance


def check_out(db: Session, user: User) -> Attendance:
    attendance = db.scalar(
        select(Attendance).where(
            Attendance.user_id == user.id,
            Attendance.date == _today(),
        ),
    )

    if attendance is None or attendance.check_in is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Check in before checking out",
        )
    if attendance.check_out is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already checked out today",
        )

    attendance.check_out = _now()
    db.commit()
    db.refresh(attendance)
    return attendance


def list_attendance(
    db: Session,
    user_id: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[Attendance]:
    query: Select[tuple[Attendance]] = select(Attendance)

    if user_id is not None:
        query = query.where(Attendance.user_id == user_id)
    if start_date is not None:
        query = query.where(Attendance.date >= start_date)
    if end_date is not None:
        query = query.where(Attendance.date <= end_date)

    query = query.order_by(Attendance.date.desc(), Attendance.id.desc())
    return list(db.scalars(query))


def list_user_attendance(
    db: Session,
    user_id: int,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[Attendance]:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return list_attendance(db, user_id=user_id, start_date=start_date, end_date=end_date)
