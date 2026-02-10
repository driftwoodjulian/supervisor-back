from backend.database import engine, SessionLocal, EvalBase
from backend.models import User
from werkzeug.security import generate_password_hash

def create_user(username, password):
    # Ensure tables exist
    EvalBase.metadata.create_all(bind=engine)
    
    session = SessionLocal()
    
    # Check if user exists
    existing_user = session.query(User).filter_by(username=username).first()
    if existing_user:
        print(f"User {username} already exists.")
        session.close()
        return

    hashed_password = generate_password_hash(password, method='scrypt')
    new_user = User(username=username, password_hash=hashed_password)
    
    session.add(new_user)
    session.commit()
    print(f"User {username} created successfully.")
    session.close()

if __name__ == "__main__":
    create_user("admin", "admin")
    create_user("testuser", "testpassword")
