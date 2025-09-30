from sqlalchemy.orm import Session
from app.core.database import get_db, Base, engine
from app.models import User, OAuth2Client


def create_test_user_and_client(db: Session):
    # ایجاد کاربر
    user = db.query(User).filter(User.username == "testuser").first()
    if not user:
        user = User(
            username="admin",
            password_hash="adminadmin",  # در تولید از bcrypt استفاده کنید
            email="admin@admin.com"
        )
        db.add(user)
        db.commit()
        print("create user.")
    else:
        print("existing user")

    # ایجاد کلاینت OAuth2
    client = db.query(OAuth2Client).filter(OAuth2Client.client_id == "client1").first()
    if not client:
        client = OAuth2Client(
            client_id="client2",
            client_secret="secret2",
            redirect_uris="http://localhost:8001/oauth/callback/",
            scopes="openid profile email"
        )
        db.add(client)
        db.commit()
        print("create client")
    else:
        print("existing client")


def main():
    # اطمینان از ایجاد جداول
    Base.metadata.create_all(bind=engine)

    # دریافت session پایگاه داده
    db_gen = get_db()
    db = next(db_gen)
    try:
        create_test_user_and_client(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()