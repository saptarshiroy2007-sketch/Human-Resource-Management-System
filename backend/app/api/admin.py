from fastapi import APIRouter, Depends

from app.core.dependencies import require_role
from app.models.user import User, UserRole


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats")
def stats(_: User = Depends(require_role(UserRole.ADMIN))) -> dict[str, int]:
    return {
        "headcount": 0,
        "pending_leaves": 0,
        "attendance_percentage_today": 0,
    }
