import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.user import User, UserRole
from app.schemas.user import UserCreate
from app.services.auth_service import create_user


DEV_USERS = [
    UserCreate(
        employee_id="ADM-001",
        email="admin@example.com",
        password="secret123",
        role=UserRole.ADMIN,
    ),
    UserCreate(
        employee_id="EMP-001",
        email="employee@example.com",
        password="secret123",
        role=UserRole.EMPLOYEE,
    ),
]


def main() -> None:
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as session:
        for user_payload in DEV_USERS:
            existing_user = session.scalar(
                select(User).where(User.email == str(user_payload.email)),
            )
            if existing_user is None:
                create_user(session, user_payload)

    print("Development database is ready.")
    print("Admin: admin@example.com / secret123")
    print("Employee: employee@example.com / secret123")


if __name__ == "__main__":
    main()
