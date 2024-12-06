from sqlalchemy.orm import Session
from ..models.base import Base
from ..models.user import User, UserRole
from ..core.security import get_password_hash
from ..core.database import engine, SessionLocal

def init_db() -> None:
    """
    Initialize the database with tables and initial data.
    """
    # Create tables
    Base.metadata.create_all(bind=engine)

    # Create initial admin user if it doesn't exist
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.email == "admin@readysetrealtor.com").first():
            admin_user = User(
                email="admin@readysetrealtor.com",
                full_name="System Administrator",
                role=UserRole.ADMIN,
                hashed_password=get_password_hash("admin123"),  # Change in production
                company_name="Ready Set Realtor",
                license_number="ADMIN-001"
            )
            db.add(admin_user)
            db.commit()
            print("Created admin user")
    finally:
        db.close()

if __name__ == "__main__":
    print("Creating initial data")
    init_db()
    print("Initial data created") 