from datetime import date, datetime

from pydantic import BaseModel, model_validator

from app.models.leave import LeaveStatus, LeaveType


class LeaveCreate(BaseModel):
    leave_type: LeaveType
    start_date: date
    end_date: date
    reason: str

    @model_validator(mode="after")
    def validate_dates(self) -> "LeaveCreate":
        if self.end_date < self.start_date:
            raise ValueError("end_date cannot be before start_date")
        return self


class LeaveReview(BaseModel):
    admin_comment: str | None = None


class LeaveOut(BaseModel):
    id: int
    user_id: int
    leave_type: LeaveType
    start_date: date
    end_date: date
    reason: str
    status: LeaveStatus
    admin_comment: str | None
    reviewed_by: int | None
    reviewed_at: datetime | None

    model_config = {"from_attributes": True}
