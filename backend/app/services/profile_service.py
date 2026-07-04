from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.profile import Profile
from app.models.user import User
from app.schemas.profile import ProfileAdminUpdate, ProfileEmployeeUpdate


def get_profile(db: Session, user_id: int) -> Profile:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    profile = db.get(Profile, user_id)
    if profile is None:
        profile = Profile(user_id=user_id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


def update_employee_profile(
    db: Session,
    user_id: int,
    payload: ProfileEmployeeUpdate,
) -> Profile:
    profile = get_profile(db, user_id)
    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile


def update_admin_profile(
    db: Session,
    user_id: int,
    payload: ProfileAdminUpdate,
) -> Profile:
    profile = get_profile(db, user_id)
    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile
