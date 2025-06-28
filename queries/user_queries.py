import secrets

from fastapi import status
from sqlalchemy.orm import Session

from auth.authentication import Auth
from models.user import User
from schema.user_schema import UserCreate, UserRead, UserSuccessResponse


class UserQueries:
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User | None:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> User | None:
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def user_exists(db: Session, email: str) -> bool:
        return db.query(User).filter(User.email == email).count() > 0

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User | None:
        user_details = user_data.model_dump()
        hashed_pw = Auth.hash_password(user_details.get("password"))
        secret_key = secrets.token_urlsafe(64)
        new_user = User(
            username=user_details.get("username"),
            email=user_details.get("email"),
            first_name=user_details.get("first_name"),
            last_name=user_details.get("last_name"),
            password_hash=hashed_pw,
            secret_key=secret_key,
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user

    @staticmethod
    def update_verified_user(user: User, db: Session):
        db.query(User).filter(User.id == user.id).update({"is_verified": True})
        db.commit()
        db.refresh(user)
