from sqlalchemy.orm import Session
from app.db import get_db, Base, engine
from app.models import User, OAuth2Client


def create_test_user_and_client(db: Session):
    # ایجاد کاربر
    user = db.query(User).filter(User.username == "testuser").first()
    if not user:
        user = User(
            username="testuser",
            password_hash="testpass",  # در تولید از bcrypt استفاده کنید
            email="test@example.com"
        )
        db.add(user)
        db.commit()
        print("کاربر 'testuser' با موفقیت ایجاد شد.")
    else:
        print("کاربر 'testuser' قبلاً وجود دارد.")

    # ایجاد کلاینت OAuth2
    client = db.query(OAuth2Client).filter(OAuth2Client.client_id == "client1").first()
    if not client:
        client = OAuth2Client(
            client_id="client1",
            client_secret="secret1",
            redirect_uris="http://localhost:8001/oauth/callback/",
            scopes="openid profile email"
        )
        db.add(client)
        db.commit()
        print("کلاینت 'client1' با موفقیت ایجاد شد.")
    else:
        print("کلاینت 'client1' قبلاً وجود دارد.")


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