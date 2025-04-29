from api.models.database import User, SessionLocal
from sqlalchemy import select

def check_user(email):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            print(f"User found: {user.email}")
            print(f"First Name: {user.first_name}")
            print(f"Last Name: {user.last_name}")
            print(f"Is Active: {user.is_active}")
        else:
            print(f"No user found with email: {email}")
    finally:
        db.close()

if __name__ == "__main__":
    check_user("amulyay.work@gmail.com") 