from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.models.user import UserRole


class AdminStatsOut(BaseModel):
    headcount: int
    pending_leaves: int
    attendance_percentage_today: int


class EmployeeListItem(BaseModel):
    id: int
    employee_id: str
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime
    department: str | None = None
    designation: str | None = None

    model_config = {"from_attributes": True}
