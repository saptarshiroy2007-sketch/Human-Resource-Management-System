from datetime import date

from pydantic import BaseModel


class ProfileEmployeeUpdate(BaseModel):
    phone: str | None = None
    address: str | None = None
    profile_pic_url: str | None = None


class ProfileAdminUpdate(ProfileEmployeeUpdate):
    department: str | None = None
    designation: str | None = None
    joining_date: date | None = None


class ProfileOut(BaseModel):
    user_id: int
    phone: str | None
    address: str | None
    department: str | None
    designation: str | None
    joining_date: date | None
    profile_pic_url: str | None

    model_config = {"from_attributes": True}
