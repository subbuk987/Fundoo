import uuid
from datetime import datetime, timedelta

import jwt

from config.config_loader import api_settings
from db.database import get_db
from exceptions.auth import InvalidToken
from models.user import User

ALGORITHM = api_settings.ALGORITHM


def create_access_token(
    data: dict, secret_key: str, expiry: timedelta = None, refresh: bool = False
):
    user_data = data.copy()
    payload = {
        "user": user_data,
        "exp": datetime.now()
        + (
            expiry
            if expiry
            else timedelta(minutes=api_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        ),
        "jti": str(uuid.uuid4()),
        "refresh": refresh,
    }

    access_token = jwt.encode(payload=payload, key=secret_key, algorithm=ALGORITHM)

    return access_token


def decode_token(token):
    token_data = jwt.decode(
        token, algorithms=[ALGORITHM], options={"verify_signature": False}
    )
    db = next(get_db())
    user = db.query(User).filter(User.id == token_data["user"]["user_id"]).first()
    db.close()

    if user is None:
        raise InvalidToken(message="Invalid token")

    verified_token_data = jwt.decode(token, key=user.secret_key, algorithms=[ALGORITHM])
    if verified_token_data["user"]["user_id"] != token_data["user"]["user_id"]:
        raise InvalidToken(message="Invalid token")

    return verified_token_data
