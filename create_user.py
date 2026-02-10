from backend.database import SessionLocal, init_db
from backend.models import User
from werkzeug.security import generate_password_hash
import sys

def create_user(username, password):
    init_db()
    session = SessionLocal()
    try:
        if session.query(User).filter_by(username=username).first():
            print(f"User '{username}' already exists.")
            return

        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, password_hash=hashed_pw)
        session.add(new_user)
        session.commit()
        print(f"User '{username}' created successfully.")
    except Exception as e:
        print(f"Error creating user: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python create_user.py <username> <password>")
        print("Creating default user 'admin' with password 'admin'")
        create_user("admin", "admin")
    else:
        create_user(sys.argv[1], sys.argv[2])
