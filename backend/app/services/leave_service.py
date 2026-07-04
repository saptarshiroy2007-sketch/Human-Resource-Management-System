from datetime import date, datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.attendance import Attendance, AttendanceStatus
from app.models.leave import LeaveRequest, LeaveStatus
from app.models.user import User
from app.schemas.leave import LeaveCreate


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _date_range(start_date: date, end_date: date) -> list[date]:
    days = (end_date - start_date).days
    return [start_date + timedelta(days=offset) for offset in range(days + 1)]


def apply_leave(db: Session, user: User, payload: LeaveCreate) -> LeaveRequest:
    leave_request = LeaveRequest(
        user_id=user.id,
        leave_type=payload.leave_type,
        start_date=payload.start_date,
        end_date=payload.end_date,
        reason=payload.reason,
        status=LeaveStatus.PENDING,
    )
    db.add(leave_request)
    db.commit()
    db.refresh(leave_request)
    return leave_request


def list_leaves(
    db: Session,
    user_id: int | None = None,
    leave_status: LeaveStatus | None = None,
) -> list[LeaveRequest]:
    query: Select[tuple[LeaveRequest]] = select(LeaveRequest)

    if user_id is not None:
        query = query.where(LeaveRequest.user_id == user_id)
    if leave_status is not None:
        query = query.where(LeaveRequest.status == leave_status)

    query = query.order_by(LeaveRequest.start_date.desc(), LeaveRequest.id.desc())
    return list(db.scalars(query))


def cancel_leave(db: Session, user: User, leave_id: int) -> None:
    leave_request = db.get(LeaveRequest, leave_id)
    if leave_request is None or leave_request.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found",
        )
    if leave_request.status != LeaveStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only pending leave requests can be cancelled",
        )

    db.delete(leave_request)
    db.commit()


def _get_pending_leave(db: Session, leave_id: int) -> LeaveRequest:
    leave_request = db.get(LeaveRequest, leave_id)
    if leave_request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found",
        )
    if leave_request.status != LeaveStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Leave request has already been reviewed",
        )
    return leave_request


def approve_leave(
    db: Session,
    leave_id: int,
    reviewer: User,
    admin_comment: str | None = None,
) -> LeaveRequest:
    leave_request = _get_pending_leave(db, leave_id)

    for leave_date in _date_range(leave_request.start_date, leave_request.end_date):
        attendance = db.scalar(
            select(Attendance).where(
                Attendance.user_id == leave_request.user_id,
                Attendance.date == leave_date,
            ),
        )

        if attendance is not None:
            if attendance.check_in is not None or attendance.check_out is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Cannot approve leave for dates with attendance activity",
                )
            attendance.status = AttendanceStatus.ON_LEAVE
        else:
            db.add(
                Attendance(
                    user_id=leave_request.user_id,
                    date=leave_date,
                    status=AttendanceStatus.ON_LEAVE,
                ),
            )

    leave_request.status = LeaveStatus.APPROVED
    leave_request.admin_comment = admin_comment
    leave_request.reviewed_by = reviewer.id
    leave_request.reviewed_at = _now()

    db.commit()
    db.refresh(leave_request)
    return leave_request


def reject_leave(
    db: Session,
    leave_id: int,
    reviewer: User,
    admin_comment: str | None = None,
) -> LeaveRequest:
    leave_request = _get_pending_leave(db, leave_id)
    leave_request.status = LeaveStatus.REJECTED
    leave_request.admin_comment = admin_comment
    leave_request.reviewed_by = reviewer.id
    leave_request.reviewed_at = _now()

    db.commit()
    db.refresh(leave_request)
    return leave_request
