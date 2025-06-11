from datetime import timedelta, datetime, timezone

import jwt
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy.sql.annotation import Annotated

from db.database import get_db
from fastapi import Depends
from auth.authentication import Auth
from exceptions.auth import AuthError
from queries.user_queries import UserQueries
from config.config_loader import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def authenticate_user(username: str, password: str,
                      db: Session = Depends(get_db())):
    user = UserQueries.get_user_by_username(db=db, username=username)
    if not user:
        return False
    if not Auth.check_password(password, user.password):
        return False

    return user


def create_access_token(data: dict, expiry: timedelta | None):
    user_data = data.copy()
    if expiry:
        expire = expiry + datetime.now(timezone.utc)
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    user_data.update({
        "exp": expire
    })
    access_token = jwt.encode(
        payload=user_data,
        key=SECRET_KEY,
        algorithm=ALGORITHM
    )

    return access_token


def get_current_user(token: str = Depends(oauth2_scheme),
                     db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise AuthError("Invalid token")
        user = UserQueries.get_user_by_username(db=db, username=username)
        if user is None:
            raise AuthError("Invalid token")
        return user
    except AuthError("Invalid token"):
        return None
