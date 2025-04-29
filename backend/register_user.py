from api.models.database import User, SessionLocal
from api.auth.router import get_password_hash

def register_user(email, password, full_name):
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"User with email {email} already exists")
            return

        # Create new user
        hashed_password = get_password_hash(password)
        new_user = User(
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
            is_active=True
        )
        db.add(new_user)
        db.commit()
        print(f"User {email} registered successfully")
    except Exception as e:
        print(f"Error registering user: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    register_user(
        email="amulyay.work@gmail.com",
        password="your_password_here",  # Replace with your desired password
        full_name="Amulya Y"
    ) 