from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, condecimal


class SalaryCreate(BaseModel):
    amount: condecimal(gt=0, max_digits=12, decimal_places=2)
    effective_date: date
    reason: str | None = None


class SalaryOut(BaseModel):
    id: int
    user_id: int
    amount: Decimal
    effective_date: date
    changed_by: int
    reason: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
