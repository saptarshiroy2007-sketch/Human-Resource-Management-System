from datetime import date, datetime

from pydantic import BaseModel

from app.models.attendance import AttendanceStatus


class AttendanceOut(BaseModel):
    id: int
    user_id: int
    date: date
    check_in: datetime | None
    check_out: datetime | None
    status: AttendanceStatus

    model_config = {"from_attributes": True}
