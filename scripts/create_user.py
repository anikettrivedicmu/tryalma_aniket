import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

def create_initial_user(db: Session) -> None:
    user = User(
        email="admin@example.com",
        hashed_password=get_password_hash("changeme"),
        is_active=True,
        is_superuser=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"Created user: {user.email}")

def main() -> None:
    db = SessionLocal()
    try:
        create_initial_user(db)
    finally:
        db.close()

if __name__ == "__main__":
    main()