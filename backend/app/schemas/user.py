from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.models.user import UserRole


class UserCreate(BaseModel):
    employee_id: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.EMPLOYEE


class UserOut(BaseModel):
    id: int
    employee_id: str
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
