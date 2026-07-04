import argparse
import getpass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.user import User, UserRole
from app.schemas.user import UserCreate
from app.services.auth_service import create_user


def _create_first_admin(db: Session, employee_id: str, email: str, password: str) -> User:
    existing_admin = db.scalar(select(User).where(User.role == UserRole.ADMIN))
    if existing_admin is not None:
        raise RuntimeError("An admin already exists; use /auth/signup from an admin account.")

    return create_user(
        db,
        UserCreate(
            employee_id=employee_id,
            email=email,
            password=password,
            role=UserRole.ADMIN,
        ),
    )


def bootstrap_admin(
    employee_id: str,
    email: str,
    password: str,
    db: Session | None = None,
) -> User:
    if db is not None:
        return _create_first_admin(db, employee_id, email, password)

    with SessionLocal() as session:
        return _create_first_admin(session, employee_id, email, password)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create the first HRMS admin account.")
    parser.add_argument("--employee-id", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--password")
    args = parser.parse_args()

    password = args.password or getpass.getpass("Admin password: ")
    user = bootstrap_admin(args.employee_id, args.email, password)
    print(f"Created admin {user.email} with employee ID {user.employee_id}")


if __name__ == "__main__":
    main()
