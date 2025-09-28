# init_db.py - Database initialization script
from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from .models import Base, User, OAuth2Client
from .auth import hash_password
import json


def init_database():
    """Initialize database with default data"""
    # Create all tables
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Create admin user if not exists
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@example.com",
                password_hash=hash_password("admin123"),
                first_name="System",
                last_name="Administrator",
                role="admin",
                status="active"
            )
            db.add(admin_user)

        # Create test users
        test_users = [
            {
                "username": "manager1",
                "email": "manager@example.com",
                "password": "manager123",
                "first_name": "John",
                "last_name": "Manager",
                "role": "manager"
            },
            {
                "username": "user1",
                "email": "user@example.com",
                "password": "user123",
                "first_name": "Jane",
                "last_name": "User",
                "role": "user"
            },
            {
                "username": "viewer1",
                "email": "viewer@example.com",
                "password": "viewer123",
                "first_name": "Bob",
                "last_name": "Viewer",
                "role": "viewer"
            }
        ]

        for user_data in test_users:
            existing_user = db.query(User).filter(User.username == user_data["username"]).first()
            if not existing_user:
                user = User(
                    username=user_data["username"],
                    email=user_data["email"],
                    password_hash=hash_password(user_data["password"]),
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                    role=user_data["role"],
                    status="active"
                )
                db.add(user)

        # Create default OAuth client
        default_client = db.query(OAuth2Client).filter(OAuth2Client.client_id == "drf_client").first()
        if not default_client:
            default_client = OAuth2Client(
                client_id="drf_client",
                client_secret="drf_secret_key_change_in_production",
                client_name="DRF Task Management Client",
                redirect_uris=json.dumps([
                    "http://localhost:8001/oauth/callback/",
                    "http://127.0.0.1:8001/oauth/callback/"
                ]),
                allowed_scopes="openid profile email",
                is_active=True
            )
            db.add(default_client)

        db.commit()
        print("Database initialized successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error initializing database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_database()